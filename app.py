import os
import numpy as np
from flask import Flask, render_template, request, send_from_directory
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['RESULT_FOLDER'] = 'static/results'

def adjust_brightness(image, brightness):
    img = np.array(image)
    brightness = int(brightness * 2.55)  # Конвертация -100..100 в -255..255
    adjusted = np.clip(img.astype(np.int32) + brightness, 0, 255).astype(np.uint8)
    return Image.fromarray(adjusted)

def create_histogram(image, filename):
    plt.figure()
    plt.title('Color Distribution')
    plt.xlabel('Intensity')
    plt.ylabel('Frequency')
    
    colors = ('red', 'green', 'blue')
    for i, color in enumerate(colors):
        histogram = np.array(image)[:,:,i].ravel()
        plt.hist(histogram, bins=256, alpha=0.7, color=color, range=(0, 256))
    
    plt.legend(['Red', 'Green', 'Blue'])
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Обработка загрузки файла
        file = request.files['image']
        brightness = int(request.form['brightness'])
        
        # Сохранение оригинального изображения
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(original_path)
        
        # Обработка изображения
        img = Image.open(original_path).convert('RGB')
        
        # Изменение яркости
        adjusted_img = adjust_brightness(img, brightness)
        adjusted_filename = f"adjusted_{brightness}_{file.filename}"
        adjusted_path = os.path.join(app.config['RESULT_FOLDER'], adjusted_filename)
        adjusted_img.save(adjusted_path)
        
        # Генерация гистограмм
        hist_original = f"hist_original_{file.filename}.png"
        hist_adjusted = f"hist_adjusted_{adjusted_filename}.png"
        
        create_histogram(img, os.path.join(app.config['RESULT_FOLDER'], hist_original))
        create_histogram(adjusted_img, os.path.join(app.config['RESULT_FOLDER'], hist_adjusted))
        
        return render_template('index.html', 
                               original=original_path,
                               adjusted=adjusted_path,
                               hist_original=os.path.join('results', hist_original),
                               hist_adjusted=os.path.join('results', hist_adjusted))
    
    return render_template('index.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)
    app.run(debug=True)