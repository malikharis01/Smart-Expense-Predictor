from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from sklearn.linear_model import LinearRegression
from typing import List

app = FastAPI(title="Smart Expense AI API")

# ====================== CORS (Required for Next.js) ======================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================== INPUT MODEL ======================
class MonthInput(BaseModel):
    month: int
    food: float
    travel: float
    shopping: float
    bills: float
    income: float

class PredictRequest(BaseModel):
    months: List[MonthInput]

# -------------------------------
# LOAD DATASET & TRAIN MODEL
# -------------------------------
data = pd.read_csv("monthly_expenses.csv")
X = data[['month', 'food', 'travel', 'shopping', 'bills', 'income']]
y = data['total_expense']

model = LinearRegression()
model.fit(X, y)
print("✅ Model trained successfully!")

# -------------------------------
# AI ADVICE FUNCTION
# -------------------------------
def generate_advice(prediction, avg_food, avg_travel, avg_shopping, avg_bills):
    advice = []
    total = prediction

    advice.append(f"📊 Your estimated next month expense is Rs {round(total, 2)}.")

    food_pct = (avg_food / total) * 100
    travel_pct = (avg_travel / total) * 100
    shopping_pct = (avg_shopping / total) * 100
    bills_pct = (avg_bills / total) * 100

    limits = {"food": 30, "travel": 20, "shopping": 25, "bills": 40}

    if food_pct > limits["food"]:
        save = avg_food - (limits["food"] / 100 * total)
        advice.append(f"🍔 Food is {round(food_pct,1)}% of your budget. Reduce it to {limits['food']}%.")
        advice.append(f"💡 You can save Rs {round(save, 2)} by controlling food expenses.")

    if travel_pct > limits["travel"]:
        save = avg_travel - (limits["travel"] / 100 * total)
        advice.append(f"🚗 Travel is {round(travel_pct,1)}% of your budget. Keep it under {limits['travel']}%.")
        advice.append(f"💡 You can save Rs {round(save, 2)} by reducing travel costs.")

    if shopping_pct > limits["shopping"]:
        save = avg_shopping - (limits["shopping"] / 100 * total)
        advice.append(f"🛍️ Shopping is {round(shopping_pct,1)}% of your budget. Limit it to {limits['shopping']}%.")
        advice.append(f"💡 You can save Rs {round(save, 2)} by cutting unnecessary shopping.")

    if bills_pct > limits["bills"]:
        save = avg_bills - (limits["bills"] / 100 * total)
        advice.append(f"⚠️ Bills are {round(bills_pct,1)}% of your budget. Try to reduce below {limits['bills']}%.")
        advice.append(f"💡 You can save Rs {round(save, 2)} by optimizing bills.")

    if total > 20000:
        advice.append("🚨 Alert: Your total expenses are quite high. Consider reducing overall spending.")

    if len(advice) <= 2:
        advice.append("✅ Great! Your spending is well balanced. Keep it up!")

    return advice

# -------------------------------
# ROUTES
# -------------------------------
@app.get("/")
def home():
    return {"message": "Smart Expense AI API is running ✅"}

@app.post("/predict")
def predict_expense(request: PredictRequest):
    months = request.months

    foods = [m.food for m in months]
    travels = [m.travel for m in months]
    shoppings = [m.shopping for m in months]
    bills_list = [m.bills for m in months]
    incomes = [m.income for m in months]

    # Graph Data
    graph_data = [
        {"month": f"Month {i+1}", "expense": foods[i] + travels[i] + shoppings[i] + bills_list[i]}
        for i in range(len(months))
    ]

    # Averages
    avg_month = sum(m.month for m in months) / len(months)
    avg_food = sum(foods) / len(foods)
    avg_travel = sum(travels) / len(travels)
    avg_shopping = sum(shoppings) / len(shoppings)
    avg_bills = sum(bills_list) / len(bills_list)
    avg_income = sum(incomes) / len(incomes)

    # Prediction
    input_data = pd.DataFrame([{
        'month': avg_month,
        'food': avg_food,
        'travel': avg_travel,
        'shopping': avg_shopping,
        'bills': avg_bills,
        'income': avg_income
    }])

    prediction = model.predict(input_data)[0]

    # Generate Advice
    advice = generate_advice(prediction, avg_food, avg_travel, avg_shopping, avg_bills)

    return {
        "prediction": round(prediction, 2),
        "graph_data": graph_data,
        "advice": advice
    }