from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
import psycopg2
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import json
import uuid
from config import settings

app = FastAPI()

DB_CONFIG = {
    "host": settings.DB_HOST,
    "database": settings.DB_NAME,
    "user": settings.DB_USER,
    "password": settings.DB_PASSWORD,
    "sslmode": settings.DB_SSLMODE,
}

class OrderItem(BaseModel):
    menuId: str
    quantity: int

class OrderRequest(BaseModel):
    user_id: str
    order_items: List[OrderItem]

@app.post("/place-order")
def place_order(order: OrderRequest):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 1. Create Order
        order_id = str(uuid.uuid4())
        created_at = datetime.utcnow()
        cursor.execute("""
            INSERT INTO "Order" (id, "userId", "status", "createdAt", "updatedAt", "totalPrice")
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (order_id, order.user_id, 'Pending', created_at, created_at, 0.0))

        # 2. Create Order Items
        for item in order.order_items:
            order_item_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO "OrderItem" (id, "orderId", "menuId", "quantity", "createdAt", "updatedAt")
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (order_item_id, order_id, item.menuId, item.quantity, created_at, created_at))

        conn.commit()

        # 3. Generate Recommendations
        df = pd.read_sql("""
            SELECT 
                o."userId" AS user_id,
                m.id AS product_id,
                m.category
            FROM "Order" o
            JOIN "OrderItem" oi ON o.id = oi."orderId"
            JOIN "Menu" m ON oi."menuId" = m.id
        """, conn)

        if df.empty or order.user_id not in df['user_id'].unique():
            conn.close()
            return {"message": "Order placed, but not enough data for recommendations."}

        pivot = pd.crosstab(df['user_id'], df['product_id'])
        user_vector = pivot.loc[order.user_id].values.reshape(1, -1)
        similarity = cosine_similarity(user_vector, pivot.values)[0]
        similar_users = pivot.index[similarity.argsort()[::-1][1:6]]
        similar_products = df[df['user_id'].isin(similar_users)]['product_id'].unique().tolist()

        # 4. Insert or update Recommendation
        recommendation_id = str(uuid.uuid4())
        now = datetime.utcnow()
        insert_query = """
            INSERT INTO "Recommendation" (id, "userId", products, "createdAt", "updatedAt")
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT ("userId") DO UPDATE SET
              products = EXCLUDED.products,
              "updatedAt" = EXCLUDED."updatedAt"
        """
        cursor.execute(insert_query, (
            recommendation_id,
            order.user_id,
            json.dumps(similar_products),
            now,
            now
        ))
        conn.commit()
        conn.close()

        return {
            "message": "Order placed successfully and recommendations updated.",
            "recommended_products": similar_products
        }

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
