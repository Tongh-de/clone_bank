"""
邮件服务
"""
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from core import config


def send_email(to_email: str, subject: str, content: str) -> dict:
    """
    发送邮件

    Args:
        to_email: 收件人邮箱
        subject: 邮件主题
        content: 邮件内容

    Returns:
        dict: {"success": bool, "message": str}
    """
    try:
        mail_host = config.EMAIL_HOST
        mail_user = config.EMAIL_USER
        mail_pass = config.EMAIL_PASS
        mail_port = config.EMAIL_PORT

        sender = config.EMAIL_USER

        message = MIMEText(content, 'plain', 'utf-8')
        message["From"] = sender
        message["To"] = to_email
        message["Subject"] = subject

        smtp = smtplib.SMTP()
        smtp.connect(mail_host, mail_port)
        smtp.login(mail_user, mail_pass)
        smtp.sendmail(sender, to_email, message.as_string())
        smtp.quit()

        return {"success": True, "message": "邮件发送成功"}
    except Exception as e:
        return {"success": False, "message": f"邮件发送失败: {str(e)}"}
