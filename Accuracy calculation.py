import pandas as pd

csv_filename = 'All Comments-Reviewed.csv'
df = pd.read_csv(csv_filename)
# print(df.columns)

column_a = df['Label']
column_b = df['Manual labeling']

differences = 0
similarities = 0
manfi = 0
mosbat = 0
khonsa = 0

for index, (value_a, value_b) in enumerate(zip(column_a, column_b)):
    if value_a == value_b:
        similarities += 1
    else:
        differences += 1
    if value_b == "منفی":
        manfi += 1
    elif value_b == "مثبت":
        mosbat += 1
    elif value_b == "خنثی":
        khonsa += 1

num_rows = df.shape[0]
accuracy = (similarities / num_rows)*100
kol = manfi + mosbat + khonsa
darsadmanfia = (manfi / num_rows)*100
darsadmosbata = (mosbat / num_rows)*100
darsadkhonsaha = (khonsa / num_rows)*100


# print(f"manfi = {manfi}")
# print(f"mosbat = {mosbat}")
# print(f"khonsa = {khonsa}")
# print(f"jame hame = {kol}")

print(f"Number of rows = {num_rows}")

print (f"darsad manfia = {darsadmanfia:.4f}")
print (f"darsad mosbata = {darsadmosbata:.4f}")
print (f"darsad khonsaha = {darsadkhonsaha:.4f}")

# print(f"Number Of Differences = {differences}")
# print(f"Number Of similarities = {similarities}")
print(f"Accuracy = {accuracy:.4f}")
