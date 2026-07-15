from pymongo import MongoClient

uri = "mongodb+srv://Ceejay:Boynova17@apexnewsninja.brwhzbz.mongodb.net/apex_news_ninja?retryWrites=true&w=majority"

client = MongoClient(
    uri,
    tls=True,
    tlsCAFile=r"C:\Users\HP\My Projects\ApexNewsNinja\ApexNewsNinja_Backend\atlas-ca.pem",
    tlsAllowInvalidCertificates=False
)

try:
    client.admin.command("ping")
    print("Connected Successfully with Python 3.12!")
except Exception as e:
    print("Connection failed:", e)
