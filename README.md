# RAGTIME (Retrieval Augmented Generation and Time-series Integration for Media Exploration)

This proof of concept (PoC) project explores the integration of textual and time-series data to unlock richer, context-aware insights that are not achievable through either data type alone. While time-series data excels at capturing trends and temporal dynamics, textual data provides qualitative context, such as user feedback, incident reports, or news articles, that often explain or augment the observed patterns.

The goal of this PoC is to design and evaluate a unified analytical framework that aligns these two modalities. By combining techniques such as natural language processing (NLP) and time-series modeling, we aim to demonstrate enhanced forecasting accuracy, anomaly detection, and interpretability across applications such as predictive maintenance, financial risk assessment, and customer sentiment tracking.

This project lays the foundation for more sophisticated, multimodal models and analytics pipelines, setting the stage for production-ready implementations in domains where both structured and unstructured data play a critical role.

#AI1st

## data sources:
### https://www.bet.hu/
### https://twelvedata.com/
### https://data.ecb.europa.eu
### https://www.cboe.com/tradable_products/vix/vix_historical_data/

## fetch data from csvs:
```python3 fetch_data.py --data_type huf --frequency D --start_date "2025-01-01 00:00:00" --end_date "2025-01-02 00:00:00" --min_jump 10.0```

## Retriever
Paste the following code to `keys.yaml`
```
openai: sk-proj...
```