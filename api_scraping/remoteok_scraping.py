import requests
import xlwt
from xlwt import Workbook
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

# Base URL for RemoteOK API
BASE_URL = "https://remoteok.com/api"

# User Agent for requests
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'

# Request Header with User Agent and Accept Language
REQUEST_HEADER = {
    'User-Agent': USER_AGENT,
    'Accept-Language': 'en-US,en;q=0.5',
}

def get_job_postings():
    """Fetch job postings from RemoteOK API."""
    try:
        res = requests.get(url=BASE_URL, headers=REQUEST_HEADER)
        res.raise_for_status()  # Raise HTTPError for bad responses
        return res.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

def output_job_to_xls(data):
    """Write job postings to an Excel file."""
    if not data:
        print("No data to write to Excel.")
        return
    
    try:
        # Create a new Workbook and add a sheet named 'job'
        wb = Workbook()
        job_sheet = wb.add_sheet('job')
        
        # Get the headers from the first item in the data list
        headers = list(data[0].keys())

        # Write the headers to the first row of the sheet
        for i in range(len(headers)):
            job_sheet.write(0, i, headers[i])
        
        # Write the data to the sheet
        for i in range(len(data)):
            job = data[i]
            values = list(job.values())

            # Truncate long strings to fit in the sheet
            for x in range(len(values)):
                if len(str(values[x])) > 32767:
                    values[x] = values[x][:32767]
                job_sheet.write(i + 1, x, str(values[x]))
        
        # Save the workbook to a file named 'remote_jobs.xls'
        wb.save('remote_jobs.xls')
        print("Data written to remote_jobs.xls")
    except Exception as e:
        print(f"Error writing data to Excel: {e}")

def send_email(send_from, send_to, subject, text, files=None,
               smtp_server='smtp.office365.com', smtp_port=587, smtp_user=None, smtp_pass=None):
    """Send an email with an attachment."""
    assert isinstance(send_to, list)

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, 'rb') as fil:
            part = MIMEApplication(fil.read(), Name=basename(f))
            part['Content-Disposition'] = f'attachment; filename="{basename(f)}"'
            msg.attach(part)

    try:
        smtp = smtplib.SMTP(smtp_server, smtp_port)
        smtp.starttls()
        smtp.login(smtp_user, smtp_pass)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.close()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

### Main program
if __name__ == "__main__":
    # Fetch job postings from RemoteOK API
    json = get_job_postings()[1:]  # Skip the first item (headers or metadata)

    # Filter only dictionary items (to avoid metadata)
    data = [job for job in json if isinstance(job, dict)]

    # Output job postings to an Excel sheet
    output_job_to_xls(data)

    # Email details
    send_from = ' victoriafrancis885@gmail.com'
    send_to = ['vicogwa@gmail.com']
    subject = 'Job Postings'
    text = 'Please find attached the list of job postings.'

    # Send the Excel file via email
    send_email(send_from, send_to, subject, text, files=['remote_jobs.xls'],
               smtp_user='victoriafrancis885@gmail.com', smtp_pass='ogwa1998')
