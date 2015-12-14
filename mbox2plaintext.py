import mailbox
import plac
import logging
logging.basicConfig(
    format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO)

import email

def get_headers(header_text, default='ascii'):
    headers = email.header.decode_header(header_text)
    header_sections = [unicode(text, charset or default) for text, charset in headers]
    return u''.join(header_sections)

def get_charset(message, default='ascii'):
    if message.get_content_charset():
        return message.get_content_charset()
    if message.get_charset():
        return message.get_charset()
    return default

def get_body(message):
    if message.is_multipart():
        body = []
        for part in email.Iterators.typed_subpart_iterator(message, 'text', 'plain'):
            charset = get_charset(part, get_charset(message))
            body.append(unicode(part.get_payload(decode=True), charset, 'replace'))
        return u'\n'.join(body).strip()
    else:
        body = unicode(message.get_payload(decode=True), get_charset(message), 'replace')
        return body.strip()

def main(mbox_file, output_dir):
    mbox = mailbox.UnixMailbox(open(mbox_file))
    counter = 0
    while True:
        msg = mbox.next()
        if not msg:
            break
        output_fname = '{0}/{1}.mbox'.format(output_dir, counter)
        with open(output_fname, 'w') as out:
            for hdr in msg.headers:
                out.write(hdr)
            out.write('\n')
            m = email.message_from_string(''.join(msg.headers + ['\n'] + msg.fp.readlines()))
            out.write(get_body(m).encode('utf-8'))

        logging.info('Saved {0}'.format(output_fname))
        counter += 1


if __name__ == '__main__':
    plac.call(main)
