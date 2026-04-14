# Booking Confirmation Email

<!-- tags: confirmation, email, booking, template, passenger, notification -->

The booking confirmation is sent automatically to the passenger after a successful reservation.

## Edit the template

1. Go to **Notifications → Booking Confirmation**.
2. Edit the **Subject** line and **Body** text.
3. Use placeholders to insert dynamic data:

| Placeholder | Output |
|-------------|--------|
| `{{passenger_name}}` | Full name of first passenger |
| `{{pnr}}` | Booking reference (PNR) |
| `{{route}}` | Origin → Destination |
| `{{departure_date}}` | Departure date and time |
| `{{total_price}}` | Total amount charged |

4. Click **Save** and **Send test email** to preview.

> ℹ️ After saving, flush the HTML cache to ensure customers see the updated version.
