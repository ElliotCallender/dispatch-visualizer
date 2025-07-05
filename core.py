import pandas as pd
import math
import re # Built-in regex module
import aiohttp
import asyncio # Built-in async module
import display_map
# also install openpyxl; pip install pandas openpyxl

INPUT_FILE = 'input_file.xlsx'
OUTPUT_FILE = 'output_file.csv'
API_KEY = 'AIzaSyDTQ-u4uYQrwsBu9owBtG4JP28y1ttcksw'

#   !!!---Difficulty algorithm------!!!
#   !!!---Difficulty algorithm------!!!
#   !!!---Difficulty algorithm------!!!

def difficulty_score(row):
    ELOs, flatbeds, screens, printers, SSDs, handScans = row['ELOs'], row['Scanner-Scales'], row['Touchscreens'], row['Epsons'], row['SSDs'], row['Hand-Scanners']
    
    # Software wait time calculation; SSD swaps are more likely to cause debugging delays
    if (ELOs + SSDs > 0):
        SW_wait = 4 * math.log(ELOs+1, 5) + 4 * math.pow(SSDs, 0.33) + 2
    else:
        SW_wait = 0

    # Hardware wait time calculation
    HW_time = (screens * 3) + (flatbeds * 2) + (ELOs * 1) + (printers * 0.6) + (SSDs * 0.5) + (handScans * 0.25)
    return SW_wait + HW_time

#   !!!---End difficulty algorithm---!!!
#   !!!---End difficulty algorithm---!!!
#   !!!---End difficulty algorithm---!!!

#   !!!---Score to color-------------!!!
#   !!!---Score to color-------------!!!
#   !!!---Score to color-------------!!!
def difficulty_color(score):
    if score < 10:
        return "blue"
    elif score < 17:
        return "green"
    elif score < 28:
        return "yellow"
    elif score < 40:
        return "orange"
    else:
        return "red"
#   !!!---End score to color----------!!!
#   !!!---End score to color----------!!!
#   !!!---End score to color----------!!!

async def main():
    df = convert_pandas()
    result_df = await get_all_coords(df)
    print(result_df)
    display_map.main(df)

def convert_pandas(input_filename=INPUT_FILE):
    rawDF = pd.read_excel(input_filename)
    
    # Check for required columns
    required_cols = ["Address", "City", "State"]
    missing_cols = [col for col in required_cols if col not in rawDF.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    df = rawDF.rename(columns={
        "Site #": "Site",
        "Install Date": "Date",
        "QTY ELO / Toshiba 767 Logic": "ELOs",
        "QTY LN7000 Debit Reader": "Debits",
        "QTY SSD": "SSDs",
        "QTY Epson Printer": "Epsons",
        "QTY Cash Drawer Cable": "Cash-Cables",
        "QTY DS8178 Hand-Held Scanner": "Hand-Scanners",
        "QTY TouchScreen and Bracket": "Touchscreens",
        "QTY Scanner Scale": "Scanner-Scales",
        "QTY Scanner Scale Calibration/ Certification": "Scale-Calibrations"
        }, inplace=False)

    for index, row in df.iterrows():
        try:
            # Check for null values
            if pd.isna(row["Address"]) or pd.isna(row["City"]) or pd.isna(row["State"]):
                print(f"Warning: Row {index} has null values")
                continue
                
            fullAddress = str(row["Address"]) + ", " + str(row["City"]) + ", " + str(row["State"])
            df.at[index, "fullAddress"] = fullAddress
            googGeocodeURL = "https://maps.googleapis.com/maps/api/geocode/json?address=" + re.sub(" ", "+", fullAddress) + "&key=" + API_KEY
            df.at[index, "googGeocodeURL"] = googGeocodeURL
            difficulty = difficulty_score(row)
            df.at[index, "difficulty"] = difficulty
            df.at[index, "difficulty_color"] = difficulty_color(difficulty)
        except Exception as e:
            print(f"Error processing row {index}: {e}")
            print(f"Row data: {row}")
            raise
    
    return df

async def get_one_coord(geocodeURL):
    async with aiohttp.ClientSession() as session:
        async with session.get(geocodeURL) as resp:
            response = await resp.json()
            if response.get("status") == "OK":
                return response["results"][0]["geometry"]["location"]
            else:
                print("Status error: " + response.get("status"))
                return None

async def get_all_coords(df):
    # Initialize the coordinates column
    df['coords'] = None
    
    async def fetch_coord(index, row):
        try:
            coord = await get_one_coord(row["googGeocodeURL"])
            return index, coord
        except Exception as e:
            print(f"Error fetching coordinates for row {index}: {e}")
            return index, None
    
    # Create tasks with proper variable capture
    tasks = []
    for index, row in df.iterrows():
        print(f"Processing index: {index} (type: {type(index)})")
        task = asyncio.create_task(fetch_coord(index, row))
        tasks.append(task)
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)
    
    # Process results and update DataFrame
    for index, coord in results:
        df.at[index, "coords"] = coord
    
    print("All addresses processed.")
    return df


if __name__ == "__main__":
    asyncio.run(main())