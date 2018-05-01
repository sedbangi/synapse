# stdlib
import socket
import logging
import ipaddress
import email.utils

# third party code
import regex

# custom code
import synapse.exc as s_exc
import synapse.lib.types as s_types
import synapse.lib.module as s_module
import synapse.lookup.iana as s_l_iana

logger = logging.getLogger(__name__)
fqdnre = regex.compile(r'^[\w._-]+$', regex.U)
cidrmasks = [((0xffffffff - (2 ** (32 - i) - 1)), (2 ** (32 - i))) for i in range(33)]


class Cidr4(s_types.Type):

    def postTypeInit(self):
        self.setNormFunc(str, self._normPyStr)

    def _normPyStr(self, valu):
        ip_str, mask_str = valu.split('/', 1)

        mask_int = int(mask_str)
        if mask_int > 32 or mask_int < 0:
            raise s_exc.BadTypeValu(valu, mesg='Invalid CIDR Mask')

        ip_int = self.modl.type('inet:ipv4').norm(ip_str)[0]

        mask = cidrmasks[mask_int]
        network = ip_int & mask[0]
        broadcast = network + mask[1] - 1
        network_str = self.modl.type('inet:ipv4').repr(network)

        norm = '{}/{}'.format(network_str, mask_int)
        info = {
            'subs': {
                'broadcast': broadcast,
                'mask': mask_int,
                'network': network,
            }
        }
        return norm, info

    def indx(self, norm):
        return norm.encode('utf8')

class Email(s_types.Type):

    def postTypeInit(self):
        self.setNormFunc(str, self._normPyStr)

    def _normPyStr(self, valu):

        user, fqdn = valu.split('@', 1)

        fqdnnorm, fqdninfo = self.modl.type('inet:fqdn').norm(fqdn)
        usernorm, userinfo = self.modl.type('inet:user').norm(user)

        norm = '%s@%s' % (usernorm, fqdnnorm)
        info = {
            'subs': {
                'fqdn': fqdnnorm,
                'user': usernorm,
            }
        }
        return norm, info

    def indx(self, norm):
        return norm.encode('utf8')

class Fqdn(s_types.Type):

    def postTypeInit(self):
        self.setNormFunc(str, self._normPyStr)

    def _normPyStr(self, valu):

        valu = valu.replace('[.]', '.')
        if not fqdnre.match(valu):
            raise s_exc.BadTypeValu(valu)

        try:
            valu = valu.encode('idna').decode('utf8').lower()
        except UnicodeError as e:
            raise s_exc.BadTypeValu(valu)

        parts = valu.split('.', 1)

        adds = []
        subs = {'host': parts[0]}

        if len(parts) == 2:
            subs['domain'] = parts[1]
        else:
            subs['sfx'] = 1

        return valu, {'subs': subs}

    def indx(self, norm):
        return norm[::-1].encode('utf8')

    def liftPropEq(self, xact, fenc, penc, text):

        valu = str(text).strip().lower()
        if not valu:
            return

        if valu[0] == '*':
            indx = valu[1:][::-1].encode('utf8')
            lops = (
                ('prop:pref', {
                    'form': fenc,
                    'prop': penc,
                    'indx': indx,
                }),
            )
            return xact.lift(lops)

        if valu.find('*') != -1:
            raise s_exc.BadLiftValu(valu=valu, mesg='Wild card may only appear at the beginning.')

        norm, info = self.norm(valu)
        indx = valu[::-1].encode('utf8')

        lops = (
            ('prop:eq', {
                'form': fenc,
                'prop': penc,
                'indx': indx,
                'valu': norm,
            }),
        )

        return xact.lift(lops)

    def repr(self, valu):
        try:
            return valu.encode('utf8').decode('idna')
        except UnicodeError as e:
            if len(valu) >= 4 and valu[0:4] == 'xn--':
                logger.exception(msg='Failed to IDNA decode ACE prefixed inet:fqdn')
                return valu
            raise  # pragma: no cover

class IPv4(s_types.Type):
    '''
    The base type for an IPv4 address.
    '''
    def postTypeInit(self):
        self.setNormFunc(str, self._normPyStr)
        self.setNormFunc(int, self._normPyInt)

    def _normPyInt(self, valu):
        norm = valu & 0xffffffff
        return norm, {}

    def _normPyStr(self, valu):
        valu = valu.replace('[.]', '.')
        byts = socket.inet_aton(valu)
        norm = int.from_bytes(byts, 'big')
        return self._normPyInt(norm)

    def indx(self, norm):
        return norm.to_bytes(4, 'big')

    def repr(self, norm):
        return socket.inet_ntoa(self.indx(norm))

    def liftPropEq(self, fenc, penc, text):

        if text.find('/') != -1:

            addr, mask = text.split('/', 1)
            norm, info = self.norm(addr)

            mask = cidrmasks[int(mask)]

            minv = norm & mask[0]

            mini = self.indx(minv)
            maxi = self.indx(minv + mask[1])

            lops = (
                ('prop:range', {
                    'prop': prop.encode('utf8'),
                    'form': form.encode('utf8'),
                    'minindx': self.indx(minv),
                    'maxindx': self.indx(minv + mask[1] - 1)
                }),
            )
            return xact.lift(lops)

        norm, info = self.norm(text)
        lops = (
            ('prop:eq', {
                'prop': prop.encode('utf8'),
                'form': form.encode('utf8'),
                'valu': norm,
                'indx': self.indx(norm),
            }),
        )
        return xact.lift(lops)

class Url(s_types.Type):
    # FIXME implement

    def postTypeInit(self):
        self.setNormFunc(str, self._normPyStr)

    def indx(self, norm):
        return norm.encode('utf8')

    def _normPyStr(self, valu):
        norm = valu
        info = {
            'subs': {}
        }
        return norm, info

class InetModule(s_module.CoreModule):

    def initCoreModule(self):
        self.model.form('inet:fqdn').onAdd(self._onAddFqdn)
        self.model.prop('inet:fqdn:zone').onSet(self._onSetFqdnZone)
        self.model.prop('inet:fqdn:iszone').onSet(self._onSetFqdnIsZone)
        self.model.prop('inet:fqdn:issuffix').onSet(self._onSetFqdnIsSuffix)

    def _onAddFqdn(self, node):

        fqdn = node.ndef[1]
        domain = node.get('domain')

        if domain is None:
            node.set('issuffix', True)
            return

        # almost certainly in the cache anyway....
        parent = node.xact.getNodeByNdef(('inet:fqdn', domain))

        if parent.get('issuffix'):
            node.set('iszone', True)
            node.set('zone', fqdn)
            return

        if parent.get('iszone'):
            node.set('zone', domain)
            return

        zone = parent.get('zone')
        if zone is not None:
            node.set('zone', zone)

    def _onSetFqdnIsSuffix(self, node, oldv):

        fqdn = node.ndef[1]

        issuffix = node.get('issuffix')
        for child in node.xact.getNodesBy('inet:fqdn:domain', fqdn):
            child.set('iszone', issuffix)

    def _onSetFqdnIsZone(self, node, oldv):

        fqdn = node.ndef[1]

        iszone = node.get('iszone')
        if iszone:
            node.set('zone', fqdn)
            return

        # we are *not* a zone and were...
        domain = node.get('domain')
        if not domain:
            node.set('zone', None)

        parent = node.xact.getNodeByNdef(('inet:fqdn', domain))
        node.set('zone', parent.get('zone'))

    def _onSetFqdnZone(self, node, oldv):

        fqdn = node.ndef[1]
        zone = node.get('zone')

        for child in node.xact.getNodesBy('inet:fqdn:domain', fqdn):

            # if they are their own zone level, skip
            if child.get('iszone'):
                continue

            # the have the same zone we do
            child.set('zone', zone)

    def getModelDefs(self):
        return (

            ('inet', {

                'ctors': (

                    ('inet:cidr4', 'synapse.models.inet.Cidr4', {}, {
                        'doc': 'An IPv4 address block in Classless Inter-Domain Routing (CIDR) notation.',
                        'ex': '1.2.3.0/24'
                    }),

                    ('inet:email', 'synapse.models.inet.Email', {}, {
                        'doc': 'An e-mail address.'}),

                    ('inet:fqdn', 'synapse.models.inet.Fqdn', {}, {
                        'doc': 'A Fully Qualified Domain Name (FQDN).',
                        'ex': 'vertex.link'}),

                    ('inet:ipv4', 'synapse.models.inet.IPv4', {}, {
                        'doc': 'An IPv4 address.',
                        'ex': '1.2.3.4'
                    }),

                    ('inet:url', 'synapse.models.inet.Url', {}, {
                        'doc': 'A Universal Resource Locator (URL).',
                        'ex': 'http://www.woot.com/files/index.html'}),

                ),

                'types': (

                    ('inet:asn', ('int', {}), {
                        'doc': 'An Autonomous System Number (ASN).'
                    }),

                    ('inet:group', ('str', {}), {
                        'doc': 'A group name string.'
                    }),

                    ('inet:passwd', ('str', {}), {
                        'doc': 'A password string.'
                    }),

                    ('inet:port', ('int', {'min': 0, 'max': 0xffff}), {
                        'doc': 'A network port.',
                        'ex': '80'
                    }),

                    ('inet:wifi:ssid', ('str', {}), {
                        'doc': 'A WiFi service set identifier (SSID) name.',
                        'ex': 'The Vertex Project'
                    }),

                    ('inet:user', ('str', {'lower': True}), {
                        'doc': 'A username string.'}),

                ),

                # NOTE: tcp4/udp4/tcp6/udp6 are going away
                'forms': (

                    # FIXME implement
                    #('inet:asn', {'ptype': 'inet:asn'}, (
                    #    ('name', {'ptype': 'str:lwr', 'defval': '??',
                    #        'doc': 'The name of the organization currently responsible for the ASN.'}),
                    #    ('owner', {'ptype': 'ou:org',
                    #        'doc': 'The guid of the organization currently responsible for the ASN.'}),
                    #)),

                    ('inet:cidr4', {}, (

                        ('broadcast', ('inet:ipv4', {}), {
                            'ro': True,
                            'doc': 'The broadcast IP address from the CIDR notation.'
                        }),

                        ('mask', ('int', {}), {
                            'ro': True,
                            'doc': 'The mask from the CIDR notation.'
                        }),

                        ('network', ('inet:ipv4', {}), {
                            'ro': True,
                            'doc': 'The network IP address from the CIDR notation.'
                        }),

                    )),

                    ('inet:email', {}, (

                        ('user', ('inet:user', {}), {
                            'ro': True,
                            'doc': 'The username of the email address.'}),

                        ('fqdn', ('inet:fqdn', {}), {
                            'ro': True,
                            'doc': 'The domain of the email address.'}),
                    )),

                    ('inet:fqdn', {}, (

                        ('created', ('time', {'ismin': True}), {
                            'doc': 'The earliest known registration (creation) date for the fqdn.'
                        }),

                        ('domain', ('inet:fqdn', {}), {
                            'doc': 'The parent domain for the FQDN.',
                        }),

                        ('expires', ('time', {'ismax': True}), {
                            'doc': 'The current expiration date for the fqdn.'
                        }),

                        ('host', ('str', {'lower': True}), {
                            'doc': 'The host part of the FQDN.',
                        }),

                        ('issuffix', ('bool', {}), {
                            'doc': 'True if the FQDN is considered a suffix.',
                            'defval': 0,
                        }),

                        ('iszone', ('bool', {}), {
                            'doc': 'True if the FQDN is considered a zone.',
                            'defval': 0,
                        }),

                        ('updated', ('time', {'ismax': True}), {
                            'doc': 'The last known updated date for the fqdn.'
                        }),

                        ('zone', ('inet:fqdn', {}), {
                            'doc': 'The zone level parent for this FQDN.',
                        }),

                    )),

                    ('inet:group', {}, ()),

                    ('inet:ipv4', {}, (
                        ('asn', ('inet:asn', {}), {
                            'defval': 0,  # FIXME replace with nullval
                            'doc': 'The ASN to which the IPv4 address is currently assigned.'
                        }),
                        # FIXME implement geospace...
                        #('latlong', ('geo:latlong', {}), {
                        #    'doc': 'The last known latitude/longitude for the node'
                        #}),
                        ('loc', ('loc', {}), {
                            'defval': '??',
                            'doc': 'The geo-political location string for the IPv4.'
                        }),
                        ('type', ('str', {}), {
                            'defval': '??',
                            'doc': 'The type of IP address (e.g., private, multicast, etc.).'
                        })
                    )),


                    # FIXME implement
                    #('inet:passwd', {'ptype': 'inet:passwd'}, [
                    #    ('md5', {'ptype': 'hash:md5', 'ro': 1,
                    #        'doc': 'The computed MD5 hash of the password.'}),
                    #    ('sha1', {'ptype': 'hash:sha1', 'ro': 1,
                    #        'doc': 'The computed SHA1 hash of the password.'}),
                    #    ('sha256', {'ptype': 'hash:sha256', 'ro': 1,
                    #        'doc': 'The computed SHA256 hash of the password.'}),
                    #]),

                    # FIXME implement inet:wifi:ssid

                    ('inet:url', {}, (
                        # FIXME implement ipv6
                        #('ipv6', ('inet:ipv6', {}), {'ro': 1,
                        #     'doc': 'The IPv6 address used in the URL.'}),
                        ('ipv4', ('inet:ipv4', {}), {'ro': 1,
                             'doc': 'The IPv4 address used in the URL (e.g., http://1.2.3.4/page.html).'}),
                        ('fqdn', ('inet:fqdn', {}), {'ro': 1,
                             'doc': 'The fqdn used in the URL (e.g., http://www.woot.com/page.html).'}),
                        ('port', ('inet:port', {}), {'ro': 1,
                             'doc': 'The port of the URL. URLs prefixed with http will be set to port 80 and '
                                 'URLs prefixed with https will be set to port 443 unless otherwise specified.'}),
                        ('user', ('inet:user', {}), {'ro': 1,
                             'doc': 'The optional username used to access the URL.'}),
                        ('passwd', ('inet:passwd', {}), {'ro': 1,
                             'doc': 'The optional password used to access the URL.'}),
                    )),

                    ('inet:user', {}, ()),

                ),
            }),
        )
