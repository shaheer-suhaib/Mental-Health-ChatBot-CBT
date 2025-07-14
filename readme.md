# 🧠 CBT Therapy Chatbot with LangGraph

An interactive CBT (Cognitive Behavioral Therapy) chatbot built using the **Gemini API**, **LangChain**, and **LangGraph**. This system simulates therapy stages with structured flow and includes tools like PHQ-9/GAD-7 assessments.

---

##  Project Flows

###  Proposed Full CBT Flow
> Full roadmap of intended features and flow structure to be implemented

![Proposed Flow](img2.jpg)

---

###  Current Implemented Flow
> What has been built and is working today

![Current Flow](image.png)



## 📁 Project Structure
```
CBT_CHATBOT/
│
├── after_experimentations/ # Conversion to code after Jupyter Notebook experiments
│ ├── CBT_State.py # Current states of our graph
│ ├── Graph.py # Graph/Tools initialization
│ └── main.py # Uses compiled graph from Graph.py and streams it
│
├── Experimentations/
│ ├── Documentation-Scripts.ipynb # Documentation/Article/AI scripts
│ └── Testing_Flow.ipynb # Initial experimentation before compilation
│
├── .gitignore
├── image.png
├── img2.jpg
└── README.md
```
text

### 🧭 Recommended File Navigation


To understand how the chatbot works:

#### Start with:
 `Experimentations/Testing_Flow.ipynb`  
*This notebook contains the early-stage design and logic testing of the CBT chatbot.*

#### Then explore:
 `after_experimentations/` folder  
*This contains the final converted Python code based on the experimental logic:*

- `CBT_State.py`: Defines state schema and tracking  
- `Graph.py`: Builds the LangGraph logic and tool nodes  
- `main.py`: Streams responses using the compiled graph

---

## 🔧 Tech Stack

| Component        | Used Tool/Library        |
|------------------|--------------------------|
| LLM              | Gemini API (Google)      |
| Framework        | LangGraph                |     
| Emotional Tools  | PHQ-9, GAD-7 (custom tools) |
| Language         | Python                   |

---

## Example Output

![Example Output](image-1.png)
