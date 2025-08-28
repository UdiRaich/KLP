from iWriter import HttpWriter   # מייבאים את המחלקה מהקובץ שלך

def main():
    writer = HttpWriter("http://127.0.0.1:8000/echo")

    data = {"username": "udi", "message": "שלום עולם"}

    for i in range(10):
        status = writer.send_data(data, "MyLaptop")
        print("POST status:", status)

if __name__ == "__main__":
    main()