```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Follow the numbers

The goal is to arrive at a basic Agent that accepts an email address and finds the orders for that customer.

```
python 7_langgraph_client_list_orders_any_customer.py <email-address>
```

```bash
python 7_langgraph_client_list_orders_any_customer.py thomashardy@example.com
```

Database includes:
franwilson@example.com
thomashardy@example.com
liuwong@example.com

The reason this is tricky is because the orders database uses a "customer_id" which is first discovered by going to the customer database to find the customer_id by searching for the contact_email address.



