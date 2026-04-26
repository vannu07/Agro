# Centralized Agricultural Constants for Krishi Mitr

INDIAN_STATES = sorted([
    "Andaman & Nicobar", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", 
    "Chandigarh", "Chhattisgarh", "Dadra & Nagar Haveli", "Daman & Diu", "Delhi", 
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jammu & Kashmir", 
    "Jharkhand", "Karnataka", "Kerala", "Lakshadweep", "Madhya Pradesh", 
    "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", 
    "Orissa", "Pondicherry", "Punjab", "Rajasthan", "Sikkim", 
    "Tamil Nadu", "Tripura", "Uttar Pradesh", "Uttaranchal", "West Bengal"
])

AGRICULTURAL_CROPS = sorted([
    "Apple", "Arecanut", "Arhar/Tur", "Bajra", "Banana", "Barley", 
    "Black pepper", "Cardamom", "Cashewnut", "Castor seed", "Coconut ", 
    "Coriander", "Cotton(lint)", "Cowpea(Lobia)", "Dry chillies", "Garlic", 
    "Ginger", "Gram", "Groundnut", "Guar seed", "Horse-gram", "Jowar", 
    "Jute", "Khesari", "Linseed", "Maize", "Mango", "Masoor", 
    "Mesta", "Moong(Green Gram)", "Moth", "Mustard", "Niger seed", 
    "Onion", "Orange", "Other Cereals", "Other Kharif pulses", "Other Rabi pulses",
    "Other Summer Pulses", "Papaya", "Peas & beans (Pulses)", "Pineapple", 
    "Pomegranate", "Potato", "Ragi", "Rapeseed & Mustard", "Rice", 
    "Safflower", "Sannhamp", "Sesamum", "Small millets", "Soyabean", 
    "Sugarcane", "Sunflower", "Sweet potato", "Tapioca", "Tobacco", 
    "Tomato", "Turmeric", "Urad", "Watermelon", "Wheat", "other oilseeds"
])

SOIL_TYPES = [
    "Alluvial Soil", "Black Soil", "Red Soil", "Laterite Soil", 
    "Desert Soil", "Mountain Soil", "Sandy Soil", "Clay Soil", "Loam Soil"
]

GROWTH_STAGES = [
    "Germination", "Seedling Stage", "Vegetative Growth", 
    "Flowering", "Pollination", "Fruit/Grain Formation", 
    "Maturation", "Harvest Ready"
]

# Mapping crops to categories for better fallback logic
CROP_CATEGORIES = {
    "Cereals": ["Rice", "Wheat", "Maize", "Bajra", "Jowar", "Ragi", "Barley", "Small millets"],
    "Pulses": ["Arhar/Tur", "Gram", "Moong(Green Gram)", "Urad", "Masoor", "Khesari", "Horse-gram", "Peas & beans (Pulses)"],
    "Oilseeds": ["Groundnut", "Sesamum", "Soyabean", "Sunflower", "Castor seed", "Linseed", "Niger seed", "Safflower", "Rapeseed & Mustard"],
    "Fruits": ["Apple", "Banana", "Mango", "Orange", "Papaya", "Pineapple", "Pomegranate", "Watermelon"],
    "Vegetables": ["Potato", "Onion", "Tomato", "Garlic", "Ginger", "Sweet potato", "Tapioca"],
    "Commercial": ["Cotton", "Jute", "Sugarcane", "Tobacco", "Mesta", "Sannhamp"],
    "Spices": ["Turmeric", "Dry chillies", "Black pepper", "Cardamom", "Coriander"],
    "Plantation": ["Coconut", "Arecanut", "Cashewnut"]
}
