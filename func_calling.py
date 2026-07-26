import smtplib, time, os   # smtplib模块主要用于处理SMTP
# email模块主要用于处理邮件的头和正文等数据
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send_email(receiver, content, subject=None):
    sender = '1879186119@qq.com'   # 发送邮箱地址
    # 构建邮件的主体对象
    msg = MIMEMultipart()

    if subject is not None:
        msg['Subject'] = subject
    else:
        msg['Subject'] = f"来自{sender}的问候邮件"

    msg['From'] = sender
    msg['To'] = receiver

    # 构建邮件的正文内容
    body = MIMEText(content, 'html', 'utf-8')
    msg.attach(body)

    # 建立与邮件服务器的连接并发送邮件
    smtpObj = smtplib.SMTP_SSL('smtp.qq.com', 465)
    smtpObj.login(user=sender, password=os.getenv("QQ_Mail_Password")) # type: ignore
    smtpObj.sendmail(sender, receiver, str(msg))
    smtpObj.quit()
    return "邮件已经成功发送到：" + receiver

functions = [
{
    "type": "function",
    "function": {
        "name": "send_email",
        "description": "向指定邮箱地址发送一封邮件",
        "parameters": {
          "type": "object",
          "properties": {
              "receiver": {
                  "type": "string",
                  "description": "邮件的收件地址",
              },
              "content": {
                  "type": "string",
                  "description": "邮件的正文内容，支持HTML格式",
              },
              "subject": {
                  "type": "string",
                  "description": "邮件的标题，如果没有标题，则可以设置为空",
              },
          },
          "required": ["receiver", "content"]   # 大模型不一定能生成邮件标题，所以设为可选
        },
    }
}
]

# 对邮件发送功能进行测试
if __name__ == '__main__':
    result = send_email("15235351314@163.com", "SMTP发送的测试邮件。")
    print(result)