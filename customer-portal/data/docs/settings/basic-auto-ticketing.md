# Auto-ticketing

<!-- tags: auto-ticketing, automatic, ticket, deadline, queue, BSP -->

Auto-ticketing issues tickets automatically at a defined time before departure, so agents don't need to manually ticket every booking.

## Enable auto-ticketing

1. Go to **Settings → Basic Settings → Auto-ticketing**.
2. Toggle **Enable auto-ticketing** to ON.
3. Set the **ticketing deadline**: how many hours before departure to ticket automatically (e.g. 24h).
4. Select the **payment method** for automatic charges.
5. Click **Save**.

## How it works

- The system checks all confirmed-but-unissued bookings every hour.
- Any booking within the deadline window is ticketed automatically.
- Agents receive a notification email for each auto-issued ticket.

> ⚠️ Ensure sufficient credit/funds are available. Failed auto-ticketing generates a queue alert.
