# services/chunk_processor.py

import requests
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import (
    OPENWEBUI_BASE_URL,
    OPENWEBUI_API_KEY,
    MODEL_NAME,
    MAX_TOKENS,
    TEMPERATURE,
    BASE_CHUNK_SIZE
)
from utils.formatter import sanitize_html, replace_markdown_bold

logger = logging.getLogger(__name__)

def create_session_with_retry(total_retries=3, backoff_factor=1):
    """
    Create a requests.Session with a retry strategy to handle transient errors.
    """
    session = requests.Session()
    retry_strategy = Retry(
        total=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def chunk_text(text, chunk_size=BASE_CHUNK_SIZE):
    """
    Splits text into chunks of approximately `chunk_size` characters.
    Tries to split on newline if possible.
    """
    text = text.strip()
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        # Optionally try to break at a newline
        newline_pos = text.rfind('\n', start, end)
        if newline_pos != -1 and newline_pos > start:
            end = newline_pos
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end
    return chunks

def call_openwebui(prompt, session=None, timeout=60):
    """
    Sends a single prompt to the OpenWebUI /chat/completions endpoint.
    Returns the content (string) or an error string if something goes wrong.
    """
    if session is None:
        session = create_session_with_retry()

    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE
    }

    try:
        response = session.post(
            f"{OPENWEBUI_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENWEBUI_API_KEY}",
                "Content-Type": "application/json"
            },
            json=data,
            timeout=timeout
        )
        response.raise_for_status()
        resp_json = response.json()
        if 'choices' in resp_json and resp_json['choices']:
            content = resp_json['choices'][0]['message']['content']
            # Clean up the content
            content = sanitize_html(content)
            content = replace_markdown_bold(content)
            return content.strip()
        else:
            logger.warning("No 'choices' in response from OpenWebUI.")
            return "No content returned."
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling OpenWebUI: {e}")
        return f"Error: {e}"

def process_chunks(
    text,
    prompt_generator_fn,
    combine_fn,
    chunk_size=BASE_CHUNK_SIZE,
    parallel=False,
    max_workers=5,
    chunk_timeout=60
):
    """
    1) Splits the text into chunks of size <= chunk_size.
    2) For each chunk, calls prompt_generator_fn(chunk, i, total_chunks)
       to build a prompt.
    3) Sends each prompt to OpenWebUI. If parallel=True, uses ThreadPoolExecutor
       with max_workers to speed up.
    4) Gathers partial results and passes them to combine_fn for a final answer.

    :param text: The large text to be processed in chunks
    :param prompt_generator_fn: Function(chunk, index, total) -> string prompt
    :param combine_fn: Function(list_of_partial_results) -> final string
    :param chunk_size: Max chunk size (defaults to BASE_CHUNK_SIZE)
    :param parallel: Whether to process chunks concurrently
    :param max_workers: Number of workers if parallel is True
    :param chunk_timeout: Timeout for each chunk request
    :return: A single string with the final combined result
    """
    # 1) Chunk the text
    chunks = chunk_text(text, chunk_size)
    if not chunks:
        return "No content to process."

    total_chunks = len(chunks)
    prompts = []
    for i, c in enumerate(chunks, start=1):
        prompt = prompt_generator_fn(c, i, total_chunks)
        prompts.append(prompt)

    # 2) Send each prompt to OpenWebUI
    session = create_session_with_retry()
    partial_results = []

    if parallel and total_chunks > 1:
        logger.debug(f"Processing {total_chunks} chunks in parallel (max_workers={max_workers})...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {
                executor.submit(call_openwebui, prompt, session, chunk_timeout): idx
                for idx, prompt in enumerate(prompts)
            }
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    result = future.result()
                    partial_results.append((idx, result))
                except Exception as e:
                    partial_results.append((idx, f"Error: {e}"))
    else:
        logger.debug(f"Processing {total_chunks} chunks sequentially...")
        for idx, prompt in enumerate(prompts):
            result = call_openwebui(prompt, session, chunk_timeout)
            partial_results.append((idx, result))

    # Sort by chunk index so final results are in correct order
    partial_results.sort(key=lambda x: x[0])
    results_in_order = [res for _, res in partial_results]

    # 3) Combine partial results
    final_result = combine_fn(results_in_order)
    return final_result

