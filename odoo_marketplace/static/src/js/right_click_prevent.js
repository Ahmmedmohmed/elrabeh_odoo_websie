/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import '@mail/models/composer_view';
import { link } from '@mail/model/model_field_command';

import { escape} from '@web/core/utils/strings';
import { url } from '@web/core/utils/urls';
registerPatch({
    name: 'ComposerView',
    recordMethods: {
      _generateMentionsLinks(body) {
            // List of mention data to insert in the body.
            // Useful to do the final replace after parsing to avoid using the
            // same tag twice if two different mentions have the same name.
            const mentions = [];
            for (const partner of this.composer.mentionedPartners) {
                const placeholder = `@-mention-partner-${partner.id}`;
                const text = `@${escape(partner.name)}`;
                mentions.push({
                    class: 'o_mail_redirect',
                    id: partner.id,
                    model: 'res.partner',
                    placeholder,
                    text,
                });
                body = body.replace(text, placeholder);
            }
            for (const channel of this.composer.mentionedChannels) {
                const placeholder = `#-mention-channel-${channel.id}`;
                const text = `#${escape(channel.name)}`;
                mentions.push({
                    class: 'o_channel_redirect',
                    id: channel.id,
                    model: 'mail.channel',
                    placeholder,
                    text,
                });
                body = body.replace(text, placeholder);
            }
            const baseHREF = url('/web');
            for (const mention of mentions) {
                const href = `href='#'`;
                const attClass = `class='${mention.class}'`;
                const dataOeId = `data-oe-id='${mention.id}'`;
                const dataOeModel = `data-oe-model='${mention.model}'`;
                const target = `target='_blank'`;
                const link = `<a ${href} ${attClass} ${dataOeId} ${dataOeModel} ${target}>${mention.text}</a>`;
                body = body.replace(mention.placeholder, link);
            }
            return body;
        },
    }
});
