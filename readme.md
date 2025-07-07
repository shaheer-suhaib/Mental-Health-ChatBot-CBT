# 🧠 CBT Therapy Chatbot with LangGraph

An interactive CBT (Cognitive Behavioral Therapy) chatbot built using the **Gemini API**, **LangChain**, and **LangGraph**. This system simulates therapy stages with structured flow, tools like PHQ-9/GAD-7, and LLM-based reasoning.

---

## 📈 Project Flows

### ✅ Proposed Full CBT Flow
> Full roadmap of intended features and flow structure    to be implemented


![proposed_CBT_FLOW drawio (1)](https://github.com/user-attachments/assets/c6a7d1d9-3190-479e-b7ca-4ec53a5e6529)

---

### ✅ Current Implemented Flow
> What has been built and is working today( streaming required)


![image](https://github.com/user-attachments/assets/b020d6ae-6e4d-496f-84a2-ebcb58555220)


---

## 🔧 Tech Stack

| Component       | Used Tool/Library        |
|----------------|--------------------------|
| LLM             | Gemini API (Google)      |
| Framework       | LangGraph                |     
| Emotional Tools | PHQ-9, GAD-7 (custom tools) |
| Language        | Python                   |

---

## 🚫 Limitations


- **Session Persistence:** While states are managed using memory, long-term storage for therapy history is not yet implemented.

---

## 🛠️ Features (Summary)

- 🧠 **ABC Model Understanding** (Activating Event, Beliefs, Consequences)
- 📊 **Emotional Check-in Node** (PHQ-9 & GAD-7)
- 🎯 **Goal Setting** with smart tracking
- 💬 **Multi-turn conversational nodes**
- 🔄 **Dynamic node transitions** via LLM routing

## Example Output
![image](https://github.com/user-attachments/assets/e3415342-db9e-4f29-a048-1b309086978c)

