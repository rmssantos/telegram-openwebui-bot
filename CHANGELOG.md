# Changelog

## **Release v2.0.0**

### **Overview**
This release introduces advanced features, enhanced security, and major performance improvements.

---

### **New Features**
1. **Summarization Overhaul**:
   - Summarizes recent group messages with admin-only access and cooldown restrictions.
   - Contextual AI summaries with labeled sections and formatting optimized for Telegram.

2. **Sentiment Analysis**:
   - Analyze group sentiment with a Fear and Greed gauge.

3. **Vision Integration**:
   - AI-based image analysis for photos sent to the bot.

4. **SQLite Migration**:
   - Persistent storage for chat history and metadata.

5. **Knowledge Base Integration**:
   - Dynamically applies knowledge bases based on detected keywords.

6. **Bing Search Integration**:
   - Search the web with `search:` commands.

---

### **Enhancements**
1. **Security**:
   - Admin-only access for critical commands.
   - Spam prevention with cooldown thresholds.

2. **Performance**:
   - Optimized SQLite database queries.
   - Improved error handling and retry mechanisms.

3. **Formatting**:
   - Telegram-compatible formatting with sanitized outputs.

4. **Docker Support**:
   - Simplified Docker setup and deployment.

---

### **Bug Fixes**
- Resolved import issues with missing modules.
- Fixed formatting inconsistencies in AI responses.
- Addressed errors in history rotation and persistence.

---

### **How to Upgrade**
1. Pull the latest changes:
   ```bash
   git pull origin main
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Rebuild Docker container (if applicable):
   ```bash
   docker-compose up --build
   ```

---

## **Previous Versions**
### **v1.1.0**:
- Summarization command overhaul with AI-driven summaries.
- Integration with Bing search for context-rich responses.

### **v1.0.0**:
- Initial release with chat, summarize, and reset commands.
