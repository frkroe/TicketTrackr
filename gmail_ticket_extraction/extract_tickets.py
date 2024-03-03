from simplegmail import Gmail
from simplegmail.query import construct_query


class Gmail_ticket_extraction():
    def __init__(self):
        # Gmail Authentification
        self.gmail = Gmail()

    def __get_ticket_label__(self, label_name:str):
        labels = self.gmail.list_labels()
        label_id = None
        for label in labels:
            if label.name == label_name:
                # label_id = label.id
                print("ID of MercaDash:", label.id)
                return label.id
                break

    def get_unread_labeled_messages(self, label_name:str):
        label_id = self.__get_ticket_label__(label_name)
        messages = self.gmail.get_unread_messages(labels= [label_id])
        print(messages)
        for message in messages:
            # print("To: " + message.recipient)
            # print("From: " + message.sender)
            print("Subject: " + message.subject)
            print("Date: " + message.date)
            # print("Preview: " + message.snippet)
            # print("Message Body: " + message.plain)  # or message.html

    def get_all_unread_inbox(self):
        messages = self.gmail.get_unread_inbox()
        if messages is not None:
            for message in messages:
                print("To: " + message.recipient)
                print("From: " + message.sender)
                print("Subject: " + message.subject)
                print("Date: " + message.date)
                print("Preview: " + message.snippet)
                print("Message Body: " + message.plain)  # or message.html
        else:
            print("no messages")

    def get_messages_with_query(self, label_name:str):
        labels = self.gmail.list_labels()
        query_params = {
            "labels":[label_name]
        }
        messages = self.gmail.get_messages(query=construct_query(query_params))      
        for message in messages:
            # print("To: " + message.recipient)
            # print("From: " + message.sender)
            print("Subject: " + message.subject)
            print("Date: " + message.date)
            # print("Preview: " + message.snippet)
            # print("Message Body: " + message.plain)  # or message.html


# Initiate Gmail Extraction Class
gmail = Gmail_ticket_extraction()

# REad all unread messages from your inbox
gmail.get_all_unread_inbox()

# 2 ways to retrieve messages with label:
gmail.get_unread_labeled_messages('MercaDash')
gmail.get_messages_with_query('MercaDash')
