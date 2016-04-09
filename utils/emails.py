from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template import loader, Context


def sendmail(to, subject, text=None, html=None, template_txt=None, template_html=None,
             attachments=None, params=None, **kwargs):
    allowed_keys = ['reply_to', 'from_email', 'cc', 'bcc', 'headers']
    diff = set(kwargs.keys()).difference(allowed_keys)
    assert not diff, "Unknown params: %s" % ', '.join(diff)
    assert to and subject, 'neither to nor subject can be empty'
    assert text or template_txt or template_html, \
        'either text or template_txt or template_html or html are required'
    params = params or {}
    attachments = attachments or []
    c = Context(params)
    if template_txt:
        t = loader.get_template(template_txt)
        text = t.render(c)
    if text:
        kwargs['body'] = text
    if template_html:
        t = loader.get_template(template_html)
        html = t.render(c)
    if isinstance(to, basestring):
        to = [to]
    mail_cls = EmailMultiAlternatives if html else EmailMessage
    email = mail_cls(subject=subject, to=to, **kwargs)
    if html:
        if attachments and isinstance(attachments[0], (tuple, list)):
            attachments = [('message.html', html, 'text/html')] + list(attachments)
        else:
            email.attach_alternative(html, "text/html")
    for attachment in attachments:
        if isinstance(attachment, basestring):
            email.attach_file(attachment)
        elif isinstance(attachment, (tuple, list)):
            email.attach(*attachment)
        else:
            raise ValueError('wrong attachment')
    email.send()
