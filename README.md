# Vendor Management System

## Introduction
The Vendor Management System is a Django-based application designed to manage vendors, track purchase orders, and calculate vendor performance metrics. This README provides an overview of the project, setup instructions, and details on using the API endpoints.

## Features
- **Vendor Profile Management:** Create, retrieve, update, and delete vendor profiles.
- **Purchase Order Tracking:** Create, retrieve, update, and delete purchase orders, and filter them by vendor.
- **Vendor Performance Evaluation:** Calculate performance metrics such as on-time delivery rate, quality rating average, response time, and fulfillment rate.

## Setup Instructions
Follow these steps to set up and run the Vendor Management System locally:

1. Clone the repository:
    ```bash
    git clone https://github.com/Tanishk04/vms.git

2. Navigate to the project directory:
    ```bash
    cd vms

3. Install dependencies:
    ```bash
    pip install -r requirements.txt

4. Apply migrations:
    ```bash
    python manage.py makemigrations
    python manage.py migrate

5. Create a Superuser
Create a superuser to access the admin panel and authenticate API endpoints:

    ```bash
    python manage.py createsuperuser

6. Run the development server:
    ```bash
    python manage.py runserver

7. Access the API at http://127.0.0.1:8000/api/

### Accessing API Endpoints
To access the API endpoints, you will need to authenticate. Follow these steps:

- Open a web browser and go to http://127.0.0.1:8000/api/.
- Log in using the superuser credentials you created earlier.
- Once logged in, you can manage users, vendors, and other data through the Django admin panel.
- To access API endpoints programmatically, you will need to include an authentication token in the request headers. You can obtain the token by logging in through the appropriate authentication endpoint (e.g., /api/token/) using your superuser credentials.


# API Endpoints
The following endpoints are available in the Vendor Management System:

### /api/vendors/

- `POST`: Create a new vendor.
- `GET`: List all vendors.
- `GET <vendor_id>`: Retrieve details of a specific vendor.
- `PUT <vendor_id>`: Update a vendor's details.
- `DELETE <vendor_id>`: Delete a vendor.

### /api/purchase_orders/

- `POST`: Create a new purchase order.
- `GET`: List all purchase orders with an option to filter by vendor.
- `GET <po_id>`: Retrieve details of a specific purchase order.
- `PUT <po_id>`: Update a purchase order.
- `DELETE <po_id>`: Delete a purchase order.

### /api/vendors/{vendor_id}/performance

- `GET`: Retrieve performance metrics for a specific vendor.

### /api/purchase_orders/{po_id}/acknowledge

- `POST`: Acknowledge a purchase order, updating acknowledgment date and triggering recalculation of average response time.

## Authentication
To access the Vendor Management System API, you need to authenticate using JSON Web Tokens (JWT). Follow these steps to obtain a JWT token:

- **Register/Login**: If you haven't already, register for an account or login using your credentials.
- **Obtain Token**: After successful login, you will receive a JWT token. You need to include this token in the header of your API requests.

## Calculating Performance Metrics with Signals

In the Vendor Management System API, we utilize Django signals to automatically calculate performance metrics based on certain events. These performance metrics include:

- **On-Time Delivery Rate**
- **Quality Rating Average**
- **Average Response Time**
- **Fulfillment Rate**

### How it Works

1. **On-Time Delivery Rate:**
   - This metric is calculated each time a purchase order status changes to 'completed'.
   - Logic: We count the number of completed purchase orders delivered on or before the delivery date and divide by the total number of completed purchase orders for that vendor.

2. **Quality Rating Average:**
   - This metric is updated upon the completion of each purchase order where a quality rating is provided .
   - Logic: We calculate the average of all quality rating values for completed purchase orders of the vendor.

3. **Average Response Time:**
   - This metric is calculated each time a purchase order is acknowledged by the vendor.
   - Logic: We compute the time difference between the issue date and acknowledgment date for each purchase order, and then find the average of these times for all purchase orders of the vendor.

4. **Fulfillment Rate:**
   - This metric is calculated upon any change in the purchase order status.
   - Logic: We divide the number of successfully fulfilled purchase orders (status 'completed' without issues) by the total number of purchase orders issued to the vendor.

### Implementation with Signals

In the codebase, we have implemented signals using Django's `post_save` signal. Whenever a relevant event occurs, such as the creation or update of a purchase order, the corresponding signal handler is triggered to recalculate the performance metrics.

The signal handlers are defined in the `signals.py` file within the respective app directories. These handlers fetch the necessary data, perform the calculations, and update the relevant fields in the associated models.

By using signals, we ensure that performance metrics are always up-to-date and automatically adjusted based on the latest data in the system.

For detailed implementation and code examples, refer to the `signals.py` files in the Vendor and Purchase Order app directories.
