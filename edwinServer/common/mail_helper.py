# -*- coding: utf-8 -*-
'''

'''
from __future__ import absolute_import
import logging
import os


class MailxMailSender(object):
    logger = logging.getLogger(__name__)

    def __init__(self):
        # read mail settings from configure file
        pass

    def _send(self, to_list, cc_list, subject, body):
        to_list.extend(cc_list)
        mailTo = ','.join(to_list)
        cmdFmt = "echo '%s' |mailx -s '%s' '%s'"
        cmd = cmdFmt % (body, subject, mailTo)
        self.logger.info("mailx cmd:%s" % cmd)
        exitcode = 0
        try:
            exitcode = os.system(cmd)
            return True
            if (exitcode != 0):
                self.logger.error("mailx exitcode =%d" % exitcode)
                return False
        except (Exception), ex:
            self.logger.exception(ex)
            return False

    def send_plain_mail(self, to_list, cc_list, subject, body):
        self.logger.info('send_plain_mail() called.')
        self._send(to_list, cc_list, subject, body)

    def send_html_mail(self, to_list, cc_list, subject, body):
        self.logger.info('send_html_mail() called.')
        self._send(to_list, cc_list, subject, body)


class LoggingMailSender(object):
    logger = logging.getLogger(__name__)

    def __init__(self):
        # read mail settings from configure file
        pass

    def _send(self, to_list, cc_list, subject, body):
        self.logger.info("""Mail sent to logging. Find details below, 
            to_list: %s 
            cc_list: %s 
            subject: %s 
            body: %s""" % (to_list, cc_list, subject, body))
        return True

    def send_plain_mail(self, to_list, cc_list, subject, body):
        self.logger.info('send_plain_mail() called.')
        self._send(to_list, cc_list, subject, body)

    def send_html_mail(self, to_list, cc_list, subject, body):
        self.logger.info('send_html_mail() called.')
        self._send(to_list, cc_list, subject, body)


class SmtpMailSender(object):
    logger = logging.getLogger(__name__)

    def __init__(self, smtp_host, smtp_port, smtp_over_ssl, mail_user, mail_pwd):
        # read mail settings from configure file
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_over_ssl = smtp_over_ssl
        self.mail_user = mail_user
        self.mail_pwd = mail_pwd

    def send_plain_mail(self, to_list, cc_list, subject, body):
        self.logger.info('send_plain_mail() called.')

        import smtplib
        from email.mime.text import MIMEText

        # Construct email
        msgRoot = MIMEText(body)
        msgRoot['Subject'] = subject
        msgRoot['From'] = self.mail_user
        msgRoot['To'] = ",".join(to_list)
        msgRoot['CC'] = ",".join(cc_list)
        #msgRoot['BCC'] =",".join(cc_list)

        try:
            if not self.smtp_over_ssl:
                if self.smtp_port == '':
                    s = smtplib.SMTP(self.smtp_host)
                else:
                    s = smtplib.SMTP(self.smtp_host, self.smtp_port)
            else:
                if self.smtp_port == '':
                    s = smtplib.SMTP_SSL(self.smtp_host)
                else:
                    s = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)

            s.set_debuglevel(True)  # print stmp actions to stdout
            if self.mail_pwd:
                s.login(self.mail_user, self.mail_pwd)

            to_addrs = to_list + cc_list
            s.sendmail(self.mail_user, to_addrs, msgRoot.as_string())
            #s.sendmail(from_addr ,to_addrs, 'test message')
            s.quit()

            self.logger.info("""Mail sent. Find details below, 
            to_list: %s 
            cc_list: %s 
            subject: %s 
            body: %s""" % (to_list, cc_list, subject, body))
            return True
        except Exception, ex:
            self.logger.exception(ex)
            return False

    def send_html_mail(self, to_list, cc_list, subject, body):
        self.logger.info('send_html_mail() called.')

        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        # Construct email
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = subject
        msgRoot['From'] = self.mail_user
        msgRoot['To'] = ",".join(to_list)
        msgRoot['CC'] = ",".join(cc_list)
        #msgRoot['BCC'] =",".join(cc_list)
        msgRoot.preamble = 'This is a multi-part message in MIME format.'

        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display.
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)

        # Add plain content
        msgText = MIMEText('This is HTML mail. If you see this message, which means you will not see the real mail content.', 'plain')
        msgAlternative.attach(msgText)

        # add html content
        msgText = MIMEText(body, 'html')
        msgAlternative.attach(msgText)

        try:
            if not self.smtp_over_ssl:
                if self.smtp_port == '':
                    s = smtplib.SMTP(self.smtp_host)
                else:
                    s = smtplib.SMTP(self.smtp_host, self.smtp_port)
            else:
                if self.smtp_port == '':
                    s = smtplib.SMTP_SSL(self.smtp_host)
                else:
                    s = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)

            s.set_debuglevel(True)  # print stmp actions to stdout
            if self.mail_pwd:
                s.login(self.mail_user, self.mail_pwd)

            to_addrs = to_list + cc_list
            s.sendmail(self.mail_user, to_addrs, msgRoot.as_string())
            #s.sendmail(from_addr ,to_addrs, 'test message')
            s.quit()

            self.logger.info("""Mail sent. Find details below, 
            to_list: %s 
            cc_list: %s 
            subject: %s 
            body: %s""" % (to_list, cc_list, subject, body))
            return True
        except Exception, ex:
            self.logger.exception(ex)
            return False
