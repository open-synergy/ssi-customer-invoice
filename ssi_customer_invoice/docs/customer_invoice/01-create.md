# Create Customer Invoice

> **Module:** ssi_customer_invoice\
> **Model:** `customer_invoice`\
> **Menu:** Financial Accounting > Account Receivable > Customer Invoice\
> **Actor:** user in group `Customer Invoice / User`\
> **State:** `—` → `draft`

## Pre-Condition

- None.

## Flow

1. Open the **Financial Accounting > Account Receivable > Customer Invoice** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Type**: Select the customer invoice type. It determines the default Journal and
     Receivable Account, and limits the Currency, Pricelist, and products allowed on
     this document.
   - **Partner**: Select the customer this invoice is issued to.
   - **Date**: Accounting date of the document. Defaults to today. Change if needed.
   - **Date Due**: Due date of the receivable. Automatically filled if **Duration** is
     selected. Change if needed.
   - **Currency**: Automatically limited to the currencies allowed by the selected
     **Type**.
   - **Pricelist**: Automatically limited to the pricelists allowed by the selected
     **Type**.
   - **Journal**: Automatically filled from **Type**. Change if needed.
   - **Receivable Account**: Automatically filled from **Type**. Change if needed.
4. Optionally fill in the other fields available in Draft status:
   - **Customer Document Number**: Reference number of the original document requested
     by the customer (e.g. their own purchase order number).
   - **Duration**: Select a predefined duration to automatically calculate **Date Due**
     from **Date**.
   - **Analytic Account**: Select the analytic account used to track the cost of this
     document.
5. On the **Detail** tab, add lines describing the products/services being invoiced.
   Repeat the following steps as many times as needed:
   - Click **Add a line**.
   - Fill in each line with:
     - **Product**: Select the product/service being invoiced.
     - **Description**: Automatically filled from **Product**. Change if needed.
     - **Usage**: Select the usage that determines the default **Account** and
       **Tax(es)** for this line.
     - **Account**: Automatically filled from **Product** and **Usage**. Change if
       needed.
     - **Analytic Account**: Optionally select the analytic account for this line.
     - **UoM**: Automatically filled from **Product**. Change if needed.
     - **Quantity**: Enter the quantity being invoiced.
     - **Price Unit**: Automatically filled from **Product**, **Pricelist**,
       **Quantity**, and **UoM**. Change if needed.
     - **Tax(es)**: Automatically filled from **Product** and **Usage**. Change if
       needed.
6. Click **Save**.

## Post-Condition

- A new record is created in **Draft** status.
- The document number is displayed as **/** until the record reaches the **Unpaid**
  status.
