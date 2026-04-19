import pandas as pd
import random

data = []


for i in range(1, 1001):
    month = (i % 12) + 1

    
    food = random.randint(3000, 6000)
    travel = random.randint(1500, 4000)
    shopping = random.randint(2000, 5000)
    bills = random.randint(5000, 9000)
    income = random.randint(25000, 50000)

 
    total_expense = food + travel + shopping + bills + random.randint(-500, 500)

    data.append([month, food, travel, shopping, bills, income, total_expense])


df = pd.DataFrame(data, columns=[
    "month", "food", "travel", "shopping", "bills", "income", "total_expense"
])


df.to_csv("monthly_expenses.csv", index=False)

print("Dataset created successfully with 1000 records!")