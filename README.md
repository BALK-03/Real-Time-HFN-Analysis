# Real-Time AI Sentiment Analysis  

## Project Overview  
This project aims to perform real-time analysis of public sentiment toward AI. The primary sentiment categories we focused on are **Hope**, **Fear**, and **Neutral**.

## Data Pipeline Architecture
![Image](https://github.com/user-attachments/assets/69f8b665-6a4a-47bb-b46e-870118b5569c)

## Project Setup  
To run the project, follow these steps:  

1. Create a `.env` file inside the `config/` folder containing your Reddit credentials. You can use the provided `config/template.env` file as a reference.  
2. Run the following command to start the project:  

   ```bash
   docker-compose up --build -d
   ```

## DistilBERT Model  
DistilBERT, a lightweight transformer model, is used for sentiment analysis due to its efficiency and multi-encoder architecture. However, the primary goal of this project is to build a **scalable and efficient data streaming infrastructure** rather than focusing on model performance. The dataset used for fine-tuning the model is not of high quality. All data is stored in the `data/` folder.
#### Classification Report:
| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| Neutral | 0.71 | 0.65 | 0.68 | 314 |
| Hope | 0.76 | 0.76 | 0.76 | 304 |
| Fear | 0.80 | 0.85 | 0.82 | 327 |
| **Accuracy** | - | - | **0.76** | **945** |
| **Macro Avg** | **0.75** | **0.75** | **0.75** | **945** |
| **Weighted Avg** | **0.75** | **0.76** | **0.75** | **945** |

#### Confusion Matrix:
|       | Neutral | Hope | Fear |
|-------|------|------|---------|
| Neutral  | 204  | 61   | 49      |
| Hope  | 50   | 232  | 22      |
| Fear | 35  | 14   | 278     |




## Grafana Dashboard
During approximately one hour of real-time streaming data, from 15:30 to 16:40, we observed that a total of 27,732 comments were processed in this experiment. These comments were classified as follows:
- 956 expressed fear toward AI.
- 2,363 expressed hope in AI.
- 18,413 were neutral.
![Image](https://github.com/user-attachments/assets/cc4fb370-16d4-4839-aa77-d91190acffe6)
