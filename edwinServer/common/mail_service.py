# -*- coding: utf-8 -*-
'''

'''


from __future__ import absolute_import
import logging
from .mail_helper import LoggingMailSender, MailxMailSender, SmtpMailSender
from .model_meta import dashboard_check_cfg
from .model_meta import team_mail_cfg
from . import conf
from . import const
import os


class MailSender(object):
    logger = logging.getLogger(__name__)

    def __init__(self):
        # TODO: set in_dev_mode=True when application debug
        self.in_dev_mode = False
        self.use_mailx_settings = conf.use_mailx_settings

        self.team_list = None
        self.currentAlarm = None
        self.currentCheckCfg = None
        self.current_itm_code = ""
        self.all_team_list = team_mail_cfg.getAllCfgInDb()

        self.logging_mail_service = LoggingMailSender()
        self.mailx_mail_service = MailxMailSender()
        self.stmp_mail_service = SmtpMailSender(conf.smtp_host,
                                                conf.smtp_port,
                                                conf.smtp_over_ssl,
                                                conf.mail_user,
                                                conf.mail_pwd)

    def _normalize_to_list(self, mailToStr):
        '''
        convert mailToString into list, and remove the duplicated mailbox
        result: list  
        '''
        mailToStr = mailToStr.lower()
        mailTo = mailToStr.replace(';', ',')
        mailTo = mailTo.split(',')
        # mailTo=list(set(mailTo))  # remove duplicate
        mailTo = map(lambda x: x.strip(), mailTo)
        mailTo = filter(lambda x: x != '', mailTo)  # remove the empty string
        return mailTo

    def filter_team_list(self):
        '''
        return the related teams to this alarm 
        '''
        team_owners = self.currentCheckCfg.owner_team_list.replace(',', ';')
        team_owner_list = team_owners.split(';')
        self.team_list = [team for team in self.all_team_list if team.owner_team_code in team_owner_list]

    def _getTeamEMailRecipients(self):
        '''
        get email boxes of related teams
        result format: []  
        '''
        mail_to = ""
        for team in self.team_list:
            mail_to = mail_to + ',' + team.email_to_list
        return self._normalize_to_list(mail_to)

    def _getWarnEMailRecipients(self):
        '''
        result format: (to_list, warning_mail_cc)  
        '''
        mailTo = self._getTeamEMailRecipients()
        mailCc = self.currentCheckCfg.warning_mail_cc
        return (mailTo, self._normalize_to_list(mailCc))

    def _getCriticalEMailRecipients(self, for_mailx=True):
        '''
        result format: (to_list, warning_mail_cc)   
        '''
        mailTo = self._getTeamEMailRecipients()
        mailCc = self.currentCheckCfg.critical_mail_cc
        return (mailTo, self._normalize_to_list(mailCc))

    def _getPhoneRecipientAndTitle(self):
        '''
        get Phone Recipient and title, the result format is [(to_1, title_1),(to_2, title_2)]  
        '''
        result = []
        for team in self.team_list:
            result.append((team.phone_mail_to, team.phone_mail_title))
        return result

    def _getSMSRecipientAndTitle(self):
        '''
        get SMS Recipient and title, the result format is [(to_1, title_1),(to_2, title_2)]  
        '''
        result = []
        for team in self.team_list:
            result.append((team.sms_mail_to, team.sms_mail_title))
        return result

    def _executeSendCmd(self, mailTo, mailCc, subject, body, html_format=False):
        if self.in_dev_mode:
            self.logging_mail_service.send_plain_mail(mailTo, mailCc, subject, body)
        else:
            if self.use_mailx_settings:
                self.mailx_mail_service.send_plain_mail(mailTo, mailCc, subject, body)
            else:
                if html_format:
                    self.stmp_mail_service.send_html_mail(mailTo, mailCc, subject, body)
                else:
                    self.stmp_mail_service.send_plain_mail(mailTo, mailCc, subject, body)

    def send(self, alarmLogObj):
        # change current objects:
        self.currentAlarm = alarmLogObj
        itm_code = alarmLogObj.itm_code
        self.current_itm_code = itm_code
        self.currentCheckCfg = dashboard_check_cfg.getCfgInDb(itm_code)
        self.filter_team_list()

        if self.currentAlarm.check_status == const.CHECK_STATUS_WARN:
            # warning alarm
            if self.currentAlarm.is_new_warning_event == 'Y':
                self.logger.info("It is a new warning alarm. It will send email.")
                self._sendByEmail()
            else:
                self.logger.info("It is a repeated warning alarm.")
                if self.currentCheckCfg.allow_repeated_mail_alarm == 'Y':
                    self._sendByEmail()
                else:
                    self.logger.info("Email repeated alarm is bypassed.")

        else:  # critical alarm
            if self.currentAlarm.is_new_critical_event == 'Y':
                self.logger.info("It is a new critical alarm. It will send email.")
                self._sendByEmail()
                if self.currentCheckCfg.critical_call_flag == 'Y':
                    self._sendByPhone()
                else:
                    self.logger.info("CallPhone alarm is disabled for this check item.")
                if self.currentCheckCfg.critical_sms_flag == 'Y':
                    self._sendBySms()
                else:
                    self.logger.info("SMS alarm is disabled for this check item.")
            else:
                self.logger.info("It is a repeated critical alarm.")
                if self.currentCheckCfg.allow_repeated_mail_alarm == 'Y':
                    self._sendByEmail()
                else:
                    self.logger.info("Email repeated alarm is bypassed.")
                if self.currentCheckCfg.critical_call_flag == 'Y' and self.currentCheckCfg.allow_repeated_call_alarm == 'Y':
                    self._sendByPhone()
                else:
                    self.logger.info("CallPhone repeated alarm is bypassed.")
                if self.currentCheckCfg.critical_sms_flag == 'Y' and self.currentCheckCfg.allow_repeated_sms_alarm == 'Y':
                    self._sendBySms()
                else:
                    self.logger.info("SMS alarm repeated is bypassed.")

    def _sendByEmail(self):
        self.logger.info("Begin to send EMail alarm.")

        if self.currentAlarm.check_status == const.CHECK_STATUS_CRITICAL:
            prefix = const.EMAIL_SUBJECT_PREFIX_CRITICAL
            (mailTo, mailCc) = self._getCriticalEMailRecipients()
        else:
            prefix = const.EMAIL_SUBJECT_PREFIX_WARN
            (mailTo, mailCc) = self._getWarnEMailRecipients()
        subject = "%s, check item: %s" % (prefix, self.currentCheckCfg.itm_title)

        msg = self.currentAlarm.check_notification_msg
        if msg is None or msg.strip() == '':
            msg = self.currentAlarm.check_detail_msg

        if self.currentAlarm.check_value:
            body = '''Please find details below, 
            <br>%s 
            <br>==================== 
            <br>Check item code :%s 
            <br>Warning limit :%s
            <br>Critical limit: %s
            <br>Current check value: %s
            <br>Current check status: %s 
            <br>Current check timestamp: %s
            <br>====================
            <br><a href="%s/items/%s" target="_blank">Click this link to find more details.</a> 
            ''' % (msg,
                   self.current_itm_code,
                   self.currentAlarm.warning_limit,
                   self.currentAlarm.critical_limit,
                   self.currentAlarm.check_value,
                   self.currentAlarm.check_status,
                   self.currentAlarm.check_timestamp,
                   conf.web_url,
                   self.currentAlarm.itm_code
                   )
        else:
            body = '''Please find details below, 
            <br>%s 
            <br>====================  
            <br>Check item code: %s 
            <br>Current check status: %s 
            <br>Current check timestamp: %s
            <br>====================
            <br><a href="%s/items/%s" target="_blank">Click this link to find more details.</a>             
            ''' % (msg,
                   self.current_itm_code,
                   self.currentAlarm.check_status,
                   self.currentAlarm.check_timestamp,
                   conf.web_url,
                   self.currentAlarm.itm_code
                   )

        self._executeSendCmd(mailTo, mailCc, subject, body, html_format=True)

        self.logger.info("End to send EMail alarm.")

    def _sendBySms(self):
        self.logger.info("Begin to send SMS alarm.")

        teams = self._getSMSRecipientAndTitle()
        for team in teams:
            (to, title) = team
            prefix = const.EMAIL_SUBJECT_PREFIX_CRITICAL
            body = "%s, check item: %s. Please check details in your mailbox. " % (prefix, self.currentCheckCfg.itm_title)
            self._executeSendCmd([to], [], title, body)

        self.logger.info("End to send SMS alarm.")

    def _sendByPhone(self):
        self.logger.info("Begin to send CallPhone alarm.")

        teams = self._getPhoneRecipientAndTitle()
        for team in teams:
            (to, title) = team
            prefix = const.EMAIL_SUBJECT_PREFIX_CRITICAL
            body = "%s, check item: %s. Please check details in your mailbox. " % (prefix, self.currentCheckCfg.itm_title)
            self._executeSendCmd([to], [], title, body)

        self.logger.info("End to send CallPhone alarm.")
