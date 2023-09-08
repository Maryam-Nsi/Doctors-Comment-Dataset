import pika
import json
import csv
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
from hazm import *
normalizer = Normalizer()

model_name = "HooshvareLab/bert-fa-base-uncased-sentiment-digikala"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
label_names = ['خنثی', 'منفی', 'مثبت']

csv_filename = "Doctors_Comment_Dataset.csv"

rabbitmq_host = 'localhost'
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()
queue = "صف_نازایی و ناباروری"
queues = channel.queue_declare(queue=queue, passive=True)

with open(csv_filename, mode="a", newline="", encoding="utf-8") as csv_file:
    csv_writer = csv.writer(csv_file)
    # csv_writer.writerow(["name", "specialty", "city", "comment", "rating", "Label", "probability"])
    
    while True:
        method_frame, properties, body = channel.basic_get(queue=queue)
        if method_frame:
            message = body.decode('utf-8')
            message_dict = json.loads(message)
            doctor_name = message_dict.get("name", "")
            doctor_city = message_dict.get("city", "")
            doctor_specialty = message_dict.get("specialty", "")
            comments = message_dict.get("comments", [])
            for comment_info in comments:
                comment_text = comment_info["comment"]
                comment_Normal = normalizer.normalize(comment_text)
                comment_Normal = normalizer.correct_spacing(comment_Normal)
                comment_Normal = normalizer.remove_diacritics(comment_Normal)
                comment_Normal = normalizer.remove_specials_chars(comment_Normal)
                comment_Normal = normalizer.decrease_repeated_chars(comment_Normal)
                comment_Normal = normalizer.persian_style(comment_Normal)
                comment_Normal = normalizer.persian_number(comment_Normal)
                comment_Normal = normalizer.unicodes_replacement(comment_Normal)
                comment_Normal = normalizer.seperate_mi(comment_Normal)
                rating = comment_info.get("rating", "")
                inputs = tokenizer(comment_Normal, return_tensors="pt", padding=True, truncation=True)
                with torch.no_grad():
                    logits = model(**inputs).logits
                    probabilities = F.softmax(logits, dim=1)
                predicted_label = label_names[torch.argmax(logits)]
                predicted_probability = probabilities[0][label_names.index(predicted_label)]
                predicted_probability_formatted = "{:.4f}".format(predicted_probability * 100)

                csv_writer.writerow([
                    doctor_name,
                    doctor_specialty,
                    doctor_city,
                    comment_text,
                    rating,
                    predicted_label,
                    predicted_probability_formatted
                ])
            
            channel.basic_ack(method_frame.delivery_tag)
        else:
            break

connection.close()
