import requests
import streamlit as st
import time

API_KEY = ""
SALE_LISTINGS_URL = "https://api.rentcast.io/v1/listings/sale"
PROPERTY_LOOKUP_URL = "https://api.rentcast.io/v1/properties"
SECRET_PASSWORD = "letmein123"

def get_sale_listings(zip_code, limit=5):
    headers = {"X-Api-Key": API_KEY}
    params = {"zipCode": zip_code, "status": "Active", "limit": limit}
    response = requests.get(SALE_LISTINGS_URL, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_owner_info(address):
    headers = {"X-Api-Key": API_KEY}
    params = {"address": address}
    response = requests.get(PROPERTY_LOOKUP_URL, headers=headers, params=params)
    if response.status_code == 404:
        return {"name": "Not Found", "mailingAddress": "N/A", "ownerOccupied": "N/A"}
    response.raise_for_status()
    data = response.json()
    if isinstance(data, list) and len(data) > 0:
        data = data[0]
    elif isinstance(data, list):
        return {"name": "Not Found", "mailingAddress": "N/A", "ownerOccupied": "N/A"}

    owner = data.get("owner", {})
    names = ", ".join(owner.get("names", [])) or "Unknown"
    mailing = owner.get("mailingAddress", {}).get("formattedAddress", "N/A")
    occupied = data.get("ownerOccupied", "N/A")
    return {"name": names, "mailingAddress": mailing, "ownerOccupied": occupied}

# Streamlit UI
st.title("🏠 Property Lookup Tool")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if password == SECRET_PASSWORD:
            st.session_state.authenticated = True
            st.success("Access granted!")
        else:
            st.error("Incorrect password.")
    st.stop()

zip_code = st.text_input("Enter ZIP Code", "90631")
max_listings = st.slider("How many properties to look up?", 1, 20, 5)

if st.button("Search Properties For Sale"):
    try:
        listings = get_sale_listings(zip_code, max_listings)
        if not listings:
            st.warning("No listings found.")
        else:
            for i, prop in enumerate(listings):
                address = prop.get("formattedAddress", "N/A")
                price = prop.get("price", "N/A")
                ptype = prop.get("propertyType", "N/A")
                bedrooms = prop.get("bedrooms", "N/A")
                bathrooms = prop.get("bathrooms", "N/A")
                sqft = prop.get("squareFootage", "N/A")
                st.subheader(f"{address}")
                st.markdown(f"**Type:** {ptype}  ")
                st.markdown(f"**Price:** ${price:,}  ")
                st.markdown(f"**Size:** {bedrooms} bd / {bathrooms} ba / {sqft} sqft")

                with st.expander("Show Owner Info"):
                    try:
                        owner = get_owner_info(address)
                        st.markdown(f"**Owner:** {owner['name']}")
                        st.markdown(f"**Mailing Address:** {owner['mailingAddress']}")
                        st.markdown(f"**Owner Occupied:** {owner['ownerOccupied']}")
                    except Exception as e:
                        st.error(f"Failed to fetch owner: {e}")

                time.sleep(0.5)  # Optional throttling to avoid rate limits

    except Exception as e:
        st.error(f"Error: {e}")
