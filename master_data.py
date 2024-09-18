import pandas as pd
import os,shutil,random,zipfile
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont


booking_data = pd.read_csv("utils/booking_data.csv")
gps_data = pd.read_csv("utils/Region_data.csv")

def generate_time_intervals(start_time, total_hours):
    intervals = []
    end_time = start_time + timedelta(hours=total_hours)
    current_time = start_time
    while current_time < end_time:
        intervals.append(current_time)
        interval_minutes = random.randint(10, 15)  # Random interval between 10 and 20 minutes
        current_time += timedelta(minutes=interval_minutes)
        
    return intervals

def generate_gps_report(start_time, total_hours, gps_data):
    intervals = generate_time_intervals(start_time, total_hours)
    gps_places = gps_data['Place'].tolist()
    gps_coords = gps_data['Coordinates'].tolist()
    report_data = []
    for time in intervals:
        random_idx = random.randint(0, len(gps_places) - 1)
        place = gps_places[random_idx]
        coordinates = gps_coords[random_idx]
        report_data.append([place, coordinates, time.strftime('%d %b %Y %H:%M')])
    return pd.DataFrame(report_data, columns=['Place', 'Coordinates', 'Time'])

def clear_folders():
    for directory in ['imgs', 'pdfs', 'report']:
        try:
            dir_path = os.path.join(os.getcwd(), directory)
            if os.path.exists(dir_path):
                for item in os.listdir(dir_path):
                    path = os.path.join(dir_path, item)
                    (os.unlink if os.path.isfile(path) or os.path.islink(path) else shutil.rmtree)(path)
        except:
            pass

def create_plot_image(df: pd.DataFrame,id,duty_date,cab_no,tota_hrs,total_kms):
    n = 3
    rows_to_use = (df.shape[0] // n) * n
    if df.shape[0] % n != 0:
        padding = pd.DataFrame([["", "", ""]] * (n - df.shape[0] % n), columns=df.columns)
        df = pd.concat([df, padding], ignore_index=True)
    def wrap_text(text, width):
        return '\n'.join([text[i:i+width] for i in range(0, len(text), width)])
    df['Place'] = df['Place'].apply(wrap_text, width=30)  # Adjust width as needed
    reshaped_data = df.values.reshape(-1, n * df.shape[1])
    reshaped_df = pd.DataFrame(reshaped_data)
    fig, ax = plt.subplots(figsize=(10, 5))  # Adjust the figsize as needed
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=reshaped_df.values, colLabels=None, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)  # Set the desired font size
    total_width = sum([0.5, 0.25, 0.25])  # Total ratio
    column_widths = [0.5/total_width, 0.25/total_width, 0.25/total_width]  # Normalize the ratios to sum to 1
    for i in range(len(reshaped_df)):
        max_height = 0
        for j in range(len(reshaped_df.columns)):
            cell = table[i, j]
            cell_height = cell.get_text().get_window_extent(renderer=fig.canvas.get_renderer()).height / fig.dpi + 0.05
            max_height = max(max_height, cell_height)
        for j in range(len(reshaped_df.columns)):
            table[i, j].set_height(max_height)
            table[i, j].set_text_props(ha='center', va='center')
            # Set column width
            table[i, j].set_width(column_widths[j % 3])

    fig.subplots_adjust(top=0.85, bottom=0.15)  # Adjust these values as needed

    plt.savefig('dataframe_image.jpg', bbox_inches='tight', dpi=300, pad_inches=0.5)  # pad_inches adds space around the image

    image_path = 'dataframe_image.jpg'
    image = Image.open(image_path)
    top_padding = 50  # Adjust the padding as needed
    bottom_padding = 50  # Adjust the padding as needed
    new_width = image.width
    new_height = image.height + top_padding + bottom_padding
    new_image = Image.new("RGB", (new_width, new_height), "white")
    new_image.paste(image, (0, top_padding))
    draw = ImageDraw.Draw(new_image)
    font = ImageFont.truetype("arial.ttf", 75)  # Adjust font size and type as needed
    draw.text((new_width / 2, 100), f"{duty_date} | {cab_no}", font=font, fill="black", anchor="mm")
    draw.text((new_width / 2, new_height - bottom_padding - 50), f"Total {total_kms} kms | Total time : {tota_hrs} Hrs", font=font, fill="black", anchor="mm")
    final_image_path = f'imgs/gr_{id}.jpg'
    new_image.save(final_image_path)

def zip_folder():
    folder_name = 'imgs'
    zip_name = f"{folder_name}.zip"
    zip_path = os.path.join(folder_name, zip_name)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_name):
            for file in files:
                file_path = os.path.join(root, file)
                # Only compress files, skip the zip file itself if it already exists
                if file != zip_name:
                    arcname = os.path.relpath(file_path, folder_name)
                    zipf.write(file_path, arcname=arcname)
    print(f"Zipped items saved in: {zip_path}")


def create_reports(booking_data, gps_data,duty_date,cab_no,tota_hrs,total_kms,regions = []):
    clear_folders()
    # regions = ['Indiranagar','MG Road']
    for _, row in booking_data.iterrows():
        booking_id = row['ID']
        start_time_str = row['PICKUP TIME'] 
        total_hours_str = row['Total Hrs']
        
        start_time = datetime.strptime(start_time_str, '%d %b %Y %H:%M')
        total_hours = int(total_hours_str.split(':')[0]) + int(total_hours_str.split(':')[1]) / 60
        if len(regions)>0:
            gps_data = gps_data[gps_data['Region'].isin(regions)]
        report_df = generate_gps_report(start_time, total_hours, gps_data)
        create_plot_image(report_df,booking_id,duty_date,cab_no,tota_hrs,total_kms)
    zip_folder()

# create_reports(booking_data.sample(5), gps_data)
# print("Done")