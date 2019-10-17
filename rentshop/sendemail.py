import smtplib, ssl


def send_email(self):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "sergiyrentshop@gmail.com"  # Enter your address
    receiver_email = "sergiy.piano@gmail.com"  # Enter receiver address
    password = 'Password2019'
    # password = input("Type your password and press enter: ")
    message = """\
    Subject: Hi there

    This message is sent from Python."""

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)







# port = 465  # For SSL
# password = input("Type your password and press enter: ")
#
# # Create a secure SSL context
# context = ssl.create_default_context()
#
# with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
#     server.login("sergiyrentshop@gmail.com", Password2019)
#     # TODO: Send email here
#
# sender_email = "my@gmail.com"
# receiver_email = "your@gmail.com"
# message = """\
# Subject: Hi there
#
# This message is sent from Python."""
#
# # Send email here
# server.sendmail(sender_email, receiver_email, message)
