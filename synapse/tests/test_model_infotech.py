import hashlib

import synapse.exc as s_exc
import synapse.common as s_common

import synapse.models.crypto as s_m_crypto

import synapse.tests.utils as s_t_utils

class InfotechModelTest(s_t_utils.SynTest):

    async def test_infotech_basics(self):

        async with self.getTestCore() as core:

            nodes = await core.nodes('''[
                it:sec:cwe=CWE-120
                    :name=omg
                    :desc=omgwtfbbq
                    :url=https://cwe.mitre.org/data/definitions/120.html
                    :parents=(CWE-119,)
            ]''')
            self.len(1, nodes)
            self.eq(nodes[0].ndef, ('it:sec:cwe', 'CWE-120'))
            self.eq(nodes[0].get('name'), 'omg')
            self.eq(nodes[0].get('desc'), 'omgwtfbbq')
            self.eq(nodes[0].get('url'), 'https://cwe.mitre.org/data/definitions/120.html')
            self.eq(nodes[0].get('parents'), ('CWE-119',))

            self.eq(r'foo\:bar', core.model.type('it:sec:cpe').norm(r'cpe:2.3:a:foo\:bar:*:*:*:*:*:*:*:*:*')[1]['subs']['vendor'])

            with self.raises(s_exc.BadTypeValu):
                nodes = await core.nodes('[it:sec:cpe=asdf]')

            with self.raises(s_exc.BadTypeValu):
                nodes = await core.nodes('[it:sec:cpe=cpe:2.3:1:2:3:4:5:6:7:8:9:10:11:12]')

            nodes = await core.nodes('[ it:sec:cpe=cpe:2.3:vertex:synapse ]')
            self.eq(nodes[0].ndef, ('it:sec:cpe', 'cpe:2.3:vertex:synapse:*:*:*:*:*:*:*:*:*'))

            nodes = await core.nodes('''[
                it:sec:cpe=cpe:2.3:a:microsoft:internet_explorer:8.0.6001:beta:*:*:*:*:*:*
            ]''')
            self.len(1, nodes)
            self.eq(nodes[0].ndef, ('it:sec:cpe', 'cpe:2.3:a:microsoft:internet_explorer:8.0.6001:beta:*:*:*:*:*:*'))
            self.eq(nodes[0].get('part'), 'a')
            self.eq(nodes[0].get('vendor'), 'microsoft')
            self.eq(nodes[0].get('product'), 'internet_explorer')
            self.eq(nodes[0].get('version'), '8.0.6001')
            self.eq(nodes[0].get('update'), 'beta')

            nodes = await core.nodes('''[
                it:mitre:attack:group=G0100
                    :org={[ ou:org=* :name=visicorp ]}
                    :name=aptvisi
                    :names=(visigroup, nerdsrus, visigroup)
                    :desc=worlddom
                    :url=https://vertex.link
                    :tag=cno.mitre.g0100
                    :references=(https://foo.com,https://bar.com)
                    :software=(S0200,S0100,S0100)
                    :isnow=G0110
                    :techniques=(T0200,T0100,T0100)
            ]''')
            self.len(1, nodes)
            self.eq(nodes[0].ndef, ('it:mitre:attack:group', 'G0100'))
            self.nn(nodes[0].get('org'))
            self.eq(nodes[0].get('name'), 'aptvisi')
            self.eq(nodes[0].get('names'), ('nerdsrus', 'visigroup'))
            self.eq(nodes[0].get('desc'), 'worlddom')
            self.eq(nodes[0].get('tag'), 'cno.mitre.g0100')
            self.eq(nodes[0].get('url'), 'https://vertex.link')
            self.eq(nodes[0].get('references'), ('https://foo.com', 'https://bar.com'))
            self.eq(nodes[0].get('software'), ('S0100', 'S0200'))
            self.eq(nodes[0].get('techniques'), ('T0100', 'T0200'))
            self.eq(nodes[0].get('isnow'), 'G0110')

            nodes = await core.nodes('''[
                it:mitre:attack:tactic=TA0100
                    :name=tactilneck
                    :desc=darkerblack
                    :url=https://archer.link
                    :tag=cno.mitre.ta0100
                    :references=(https://foo.com,https://bar.com)
                    :matrix=enterprise
            ]''')
            self.len(1, nodes)
            self.eq(nodes[0].ndef, ('it:mitre:attack:tactic', 'TA0100'))
            self.eq(nodes[0].get('name'), 'tactilneck')
            self.eq(nodes[0].get('desc'), 'darkerblack')
            self.eq(nodes[0].get('tag'), 'cno.mitre.ta0100')
            self.eq(nodes[0].get('url'), 'https://archer.link')
            self.eq(nodes[0].get('references'), ('https://foo.com', 'https://bar.com'))
            self.eq(nodes[0].get('matrix'), 'enterprise')

            nodes = await core.nodes('''[
                it:mitre:attack:technique=T0100
                    :name=lockpicking
                    :desc=speedhackers
                    :url=https://locksrus.link
                    :tag=cno.mitre.t0100
                    :references=(https://foo.com,https://bar.com)
                    :parent=T9999
                    :status=deprecated
                    :isnow=T1110
                    :tactics=(TA0200,TA0100,TA0100)
                    :matrix=enterprise
            ]''')
            self.len(1, nodes)
            self.eq(nodes[0].ndef, ('it:mitre:attack:technique', 'T0100'))
            self.eq(nodes[0].get('name'), 'lockpicking')
            self.eq(nodes[0].get('desc'), 'speedhackers')
            self.eq(nodes[0].get('tag'), 'cno.mitre.t0100')
            self.eq(nodes[0].get('url'), 'https://locksrus.link')
            self.eq(nodes[0].get('references'), ('https://foo.com', 'https://bar.com'))
            self.eq(nodes[0].get('parent'), 'T9999')
            self.eq(nodes[0].get('tactics'), ('TA0100', 'TA0200'))
            self.eq(nodes[0].get('status'), 'deprecated')
            self.eq(nodes[0].get('isnow'), 'T1110')
            self.eq(nodes[0].get('matrix'), 'enterprise')

            nodes = await core.nodes('''[
                it:mitre:attack:software=S0100
                    :software=*
                    :name=redtree
                    :names=("redtree alt", eviltree)
                    :desc=redtreestuff
                    :url=https://redtree.link
                    :tag=cno.mitre.s0100
                    :references=(https://foo.com,https://bar.com)
                    :techniques=(T0200,T0100,T0100)
                    :isnow=S0110
            ]''')
            self.len(1, nodes)
            self.eq(nodes[0].ndef, ('it:mitre:attack:software', 'S0100'))
            self.nn(nodes[0].get('software'))
            self.eq(nodes[0].get('name'), 'redtree')
            self.eq(nodes[0].get('names'), ('eviltree', 'redtree alt'))
            self.eq(nodes[0].get('desc'), 'redtreestuff')
            self.eq(nodes[0].get('tag'), 'cno.mitre.s0100')
            self.eq(nodes[0].get('url'), 'https://redtree.link')
            self.eq(nodes[0].get('references'), ('https://foo.com', 'https://bar.com'))
            self.eq(nodes[0].get('techniques'), ('T0100', 'T0200'))
            self.eq(nodes[0].get('isnow'), 'S0110')
            self.len(3, await core.nodes('it:prod:softname=redtree -> it:mitre:attack:software -> it:prod:softname'))

            nodes = await core.nodes('''[
                it:mitre:attack:mitigation=M0100
                    :name=patchstuff
                    :desc=patchyourstuff
                    :url=https://wsus.com
                    :tag=cno.mitre.m0100
                    :references=(https://foo.com,https://bar.com)
                    :addresses=(T0200,T0100,T0100)
                    :matrix=enterprise
            ]''')
            self.len(1, nodes)
            self.eq(nodes[0].ndef, ('it:mitre:attack:mitigation', 'M0100'))
            self.eq(nodes[0].get('name'), 'patchstuff')
            self.eq(nodes[0].get('desc'), 'patchyourstuff')
            self.eq(nodes[0].get('tag'), 'cno.mitre.m0100')
            self.eq(nodes[0].get('url'), 'https://wsus.com')
            self.eq(nodes[0].get('references'), ('https://foo.com', 'https://bar.com'))
            self.eq(nodes[0].get('addresses'), ('T0100', 'T0200'))
            self.eq(nodes[0].get('matrix'), 'enterprise')

            nodes = await core.nodes('''[
                it:exec:thread=*
                    :proc=*
                    :created=20210202
                    :exited=20210203
                    :exitcode=0
                    :src:proc=*
                    :src:thread=*
                    :sandbox:file=*
            ]''')
            self.len(1, nodes)
            self.nn(nodes[0].ndef[1])
            self.eq(nodes[0].get('created'), 1612224000000)
            self.eq(nodes[0].get('exited'), 1612310400000)
            self.eq(nodes[0].get('exitcode'), 0)
            self.len(1, await core.nodes('it:exec:thread:created :proc -> it:exec:proc'))
            self.len(1, await core.nodes('it:exec:thread:created :src:proc -> it:exec:proc'))
            self.len(1, await core.nodes('it:exec:thread:created :src:thread -> it:exec:thread'))
            self.len(1, await core.nodes('it:exec:thread:created :sandbox:file -> file:bytes'))

            nodes = await core.nodes('''[
                it:exec:loadlib=*
                    :proc=*
                    :va=0x00a000
                    :loaded=20210202
                    :unloaded=20210203
                    :path=/home/invisigoth/rootkit.so
                    :file=*
                    :sandbox:file=*
            ]''')
            self.len(1, nodes)
            self.nn(nodes[0].ndef[1])
            self.nn(nodes[0].get('proc'))
            self.eq(nodes[0].get('va'), 0x00a000)
            self.eq(nodes[0].get('loaded'), 1612224000000)
            self.eq(nodes[0].get('unloaded'), 1612310400000)
            self.len(1, await core.nodes('it:exec:loadlib :file -> file:bytes'))
            self.len(1, await core.nodes('it:exec:loadlib :proc -> it:exec:proc'))
            self.len(1, await core.nodes('it:exec:loadlib -> file:path +file:path=/home/invisigoth/rootkit.so'))
            self.len(1, await core.nodes('it:exec:loadlib :sandbox:file -> file:bytes'))

            nodes = await core.nodes('''[
                it:exec:mmap=*
                    :proc=*
                    :va=0x00a000
                    :size=4096
                    :perms:read=1
                    :perms:write=0
                    :perms:execute=1
                    :created=20210202
                    :deleted=20210203
                    :path=/home/invisigoth/rootkit.so
                    :hash:sha256=ad9f4fe922b61e674a09530831759843b1880381de686a43460a76864ca0340c
                    :sandbox:file=*
            ]''')
            self.len(1, nodes)
            self.nn(nodes[0].ndef[1])
            self.nn(nodes[0].get('proc'))
            self.eq(nodes[0].get('va'), 0x00a000)
            self.eq(nodes[0].get('size'), 4096)
            self.eq(nodes[0].get('perms:read'), 1)
            self.eq(nodes[0].get('perms:write'), 0)
            self.eq(nodes[0].get('perms:execute'), 1)
            self.eq(nodes[0].get('created'), 1612224000000)
            self.eq(nodes[0].get('deleted'), 1612310400000)
            self.eq(nodes[0].get('hash:sha256'), 'ad9f4fe922b61e674a09530831759843b1880381de686a43460a76864ca0340c')
            self.len(1, await core.nodes('it:exec:mmap -> hash:sha256'))
            self.len(1, await core.nodes('it:exec:mmap :proc -> it:exec:proc'))
            self.len(1, await core.nodes('it:exec:mmap -> file:path +file:path=/home/invisigoth/rootkit.so'))
            self.len(1, await core.nodes('it:exec:mmap :sandbox:file -> file:bytes'))

            nodes = await core.nodes('''[
                it:exec:proc=80e6c59d9c349ac15f716eaa825a23fa
                    :killedby=*
                    :exitcode=0
                    :exited=20210202
                    :sandbox:file=*
                    :name=RunDLL32
                    :path=c:/windows/system32/rundll32.exe
            ]''')
            self.len(1, nodes)
            self.eq(nodes[0].ndef[1], '80e6c59d9c349ac15f716eaa825a23fa')
            self.nn(nodes[0].get('killedby'))
            self.eq(nodes[0].get('exitcode'), 0)
            self.eq(nodes[0].get('exited'), 1612224000000)
            self.eq(nodes[0].get('name'), 'RunDLL32')
            self.eq(nodes[0].get('path'), 'c:/windows/system32/rundll32.exe')
            self.eq(nodes[0].get('path:base'), 'rundll32.exe')
            self.len(1, await core.nodes('it:exec:proc=80e6c59d9c349ac15f716eaa825a23fa :killedby -> it:exec:proc'))
            self.len(1, await core.nodes('it:exec:proc=80e6c59d9c349ac15f716eaa825a23fa :sandbox:file -> file:bytes'))

            nodes = await core.nodes('''[
                it:av:prochit=*
                    :proc=*
                    :sig=(a6834cea191af070abb11af59d881c40, 'foobar')
                    :time=20210202
            ]''')
            self.len(1, nodes)
            self.nn(nodes[0].ndef[1])
            self.nn(nodes[0].get('proc'))
            self.eq(nodes[0].get('sig'), ('a6834cea191af070abb11af59d881c40', 'foobar'))
            self.eq(nodes[0].get('time'), 1612224000000)
            self.len(1, await core.nodes('it:av:prochit -> it:av:sig'))
            self.len(1, await core.nodes('it:av:prochit -> it:exec:proc'))
            self.len(1, await core.nodes('it:av:signame=foobar -> it:av:sig'))

            nodes = await core.nodes('''[
                it:app:yara:procmatch=*
                    :proc=*
                    :rule=*
                    :time=20210202
            ]''')
            self.len(1, nodes)
            self.nn(nodes[0].ndef[1])
            self.nn(nodes[0].get('proc'))
            self.nn(nodes[0].get('rule'))
            self.eq(nodes[0].get('time'), 1612224000000)
            self.len(1, await core.nodes('it:app:yara:procmatch -> it:exec:proc'))
            self.len(1, await core.nodes('it:app:yara:procmatch -> it:app:yara:rule'))

            nodes = await core.nodes('''[
                it:av:scan:result=*
                    :time=20231117
                    :verdict=suspicious
                    :scanner={[ it:prod:softver=* :name="visi scan" ]}
                    :scanner:name="visi scan"
                    :signame=omgwtfbbq
                    :target:file=*
                    :target:proc={[ it:exec:proc=* :cmd="foo.exe --bar" ]}
                    :target:host={[ it:host=* :name=visihost ]}
                    :target:fqdn=vertex.link
                    :target:url=https://vertex.link
                    :target:ipv4=1.2.3.4
                    :target:ipv6='::1'
                    :multi:scan={[ it:av:scan:result=*
                        :scanner:name="visi total"
                        :multi:count=10
                        :multi:count:benign=3
                        :multi:count:unknown=1
                        :multi:count:suspicious=4
                        :multi:count:malicious=2
                    ]}
            ]''')
            self.eq(1700179200000, nodes[0].get('time'))
            self.eq(30, nodes[0].get('verdict'))
            self.eq('visi scan', nodes[0].get('scanner:name'))
            self.eq('vertex.link', nodes[0].get('target:fqdn'))
            self.eq('https://vertex.link', nodes[0].get('target:url'))
            self.eq(0x01020304, nodes[0].get('target:ipv4'))
            self.eq('::1', nodes[0].get('target:ipv6'))
            self.eq('omgwtfbbq', nodes[0].get('signame'))

            self.len(1, await core.nodes('it:av:scan:result:scanner:name="visi scan" -> it:host'))
            self.len(1, await core.nodes('it:av:scan:result:scanner:name="visi scan" -> inet:url'))
            self.len(1, await core.nodes('it:av:scan:result:scanner:name="visi scan" -> inet:fqdn'))
            self.len(1, await core.nodes('it:av:scan:result:scanner:name="visi scan" -> file:bytes'))
            self.len(1, await core.nodes('it:av:scan:result:scanner:name="visi scan" -> it:exec:proc'))
            self.len(1, await core.nodes('it:av:scan:result:scanner:name="visi scan" -> it:av:signame'))
            self.len(1, await core.nodes('it:av:scan:result:scanner:name="visi scan" -> it:prod:softver'))
            self.len(1, await core.nodes('it:av:scan:result:scanner:name="visi scan" -> it:prod:softname'))

            nodes = await core.nodes('it:av:scan:result:scanner:name="visi total"')
            self.len(1, nodes)

            self.eq(10, nodes[0].get('multi:count'))
            self.eq(3, nodes[0].get('multi:count:benign'))
            self.eq(1, nodes[0].get('multi:count:unknown'))
            self.eq(4, nodes[0].get('multi:count:suspicious'))
            self.eq(2, nodes[0].get('multi:count:malicious'))

            self.len(1, await core.nodes('it:av:scan:result:scanner:name="visi total" -> it:av:scan:result +:scanner:name="visi scan"'))

    async def test_infotech_ios(self):

        async with self.getTestCore() as core:

            async with await core.snap() as snap:

                valu = '00000000-0000-0000-0000-00000000000A'
                idfa = await snap.addNode('it:os:ios:idfa', valu)
                self.eq(idfa.ndef[1], '00000000-0000-0000-0000-00000000000a')

    async def test_infotech_android(self):

        softver = s_common.guid()

        async with self.getTestCore() as core:

            async with await core.snap() as snap:

                perm = await snap.addNode('it:os:android:perm', 'Foo Perm')
                self.eq(perm.ndef[1], 'Foo Perm')
                intent = await snap.addNode('it:os:android:intent', 'Foo Intent')
                self.eq(intent.ndef[1], 'Foo Intent')

                ilisn = await snap.addNode('it:os:android:ilisten', (softver, 'Listen Test'))
                self.eq(ilisn.get('app'), softver)
                self.eq(ilisn.get('intent'), 'Listen Test')

                ibcast = await snap.addNode('it:os:android:ibroadcast', (softver, 'Broadcast Test'))
                self.eq(ibcast.get('app'), softver)
                self.eq(ibcast.get('intent'), 'Broadcast Test')

                reqperm = await snap.addNode('it:os:android:reqperm', (softver, 'Test Perm'))
                self.eq(reqperm.get('app'), softver)
                self.eq(reqperm.get('perm'), 'Test Perm')

                valu = 'someIdentifier'
                aaid = await snap.addNode('it:os:android:aaid', valu)
                self.eq(aaid.ndef[1], 'someidentifier')

    async def test_it_forms_simple(self):
        async with self.getTestCore() as core:
            place = s_common.guid()
            async with await core.snap() as snap:
                node = await snap.addNode('it:hostname', 'Bobs Computer')
                self.eq(node.ndef[1], 'bobs computer')
                org0 = s_common.guid()
                host0 = s_common.guid()
                sver0 = s_common.guid()
                cont0 = s_common.guid()
                hprops = {
                    'name': 'Bobs laptop',
                    'desc': 'Bobs paperweight',
                    'ipv4': '1.2.3.4',
                    'latlong': '0.0, 0.0',
                    'place': place,
                    'os': sver0,
                    'manu': 'Dull',
                    'model': 'Lutitude 8249',
                    'serial': '111-222',
                    'loc': 'us.hehe.haha',
                    'operator': cont0,
                    'org': org0,
                    'ext:id': 'foo123'
                }
                node = await snap.addNode('it:host', host0, hprops)
                self.eq(node.ndef[1], host0)
                self.eq(node.get('name'), 'bobs laptop')
                self.eq(node.get('desc'), 'Bobs paperweight')
                self.eq(node.get('ipv4'), 0x01020304)
                self.eq(node.get('latlong'), (0.0, 0.0))
                self.eq(node.get('place'), place)
                self.eq(node.get('os'), sver0)
                self.eq(node.get('loc'), 'us.hehe.haha')
                self.eq(node.get('org'), org0)
                self.eq(node.get('operator'), cont0)
                self.eq(node.get('ext:id'), 'foo123')

                node = await snap.addNode('it:hosturl', (host0, 'http://vertex.ninja/cool.php'))
                self.eq(node.ndef[1], (host0, 'http://vertex.ninja/cool.php'))
                self.eq(node.get('host'), host0)
                self.eq(node.get('url'), 'http://vertex.ninja/cool.php')

                node = await snap.addNode('it:dev:int', 0x61C88648)
                self.eq(node.ndef[1], 1640531528)

                cprops = {
                    'desc': 'Some words.',
                }
                node = await snap.addNode('it:sec:cve', 'CVE-2013-9999', cprops)
                self.eq(node.ndef[1], 'cve-2013-9999')
                self.eq(node.get('desc'), 'Some words.')

                node = await snap.addNode('it:sec:cve', 'CVE\u20122013\u20131138', cprops)
                self.eq(node.ndef[1], 'cve-2013-1138')

                node = await snap.addNode('it:sec:cve', 'CVE\u20112013\u20140001', cprops)
                self.eq(node.ndef[1], 'cve-2013-0001')

                hash0 = s_common.guid()
                hprops = {
                    'salt': 'B33F',
                    'hash:md5': s_m_crypto.ex_md5,
                    'hash:sha1': s_m_crypto.ex_sha1,
                    'hash:sha256': s_m_crypto.ex_sha256,
                    'hash:sha512': s_m_crypto.ex_sha512,
                    'hash:lm': s_m_crypto.ex_md5,
                    'hash:ntlm': s_m_crypto.ex_md5,
                    'passwd': "I've got the same combination on my luggage!",
                }
                node = await snap.addNode('it:auth:passwdhash', hash0, hprops)
                self.eq(node.ndef[1], hash0)
                self.eq(node.get('salt'), 'b33f')
                self.eq(node.get('hash:md5'), s_m_crypto.ex_md5)
                self.eq(node.get('hash:sha1'), s_m_crypto.ex_sha1)
                self.eq(node.get('hash:sha256'), s_m_crypto.ex_sha256)
                self.eq(node.get('hash:sha512'), s_m_crypto.ex_sha512)
                self.eq(node.get('hash:lm'), s_m_crypto.ex_md5)
                self.eq(node.get('hash:ntlm'), s_m_crypto.ex_md5)
                self.eq(node.get('passwd'), "I've got the same combination on my luggage!")

            nodes = await core.nodes('[ it:adid=visi ]')
            self.eq(('it:adid', 'visi'), nodes[0].ndef)

            nodes = await core.nodes('''
                init {
                    $org = $lib.guid()
                    $host = $lib.guid()
                    $acct = $lib.guid()
                }
                [
                    it:account=$acct
                        :host=$host
                        :user=visi
                        :contact={[ ps:contact=* :email=visi@vertex.link ]}
                        :domain={[ it:domain=* :org=$org :name=vertex :desc="the vertex project domain" ]}

                    (it:logon=* :time=20210314 :logoff:time=202103140201 :account=$acct :host=$host :duration=(:logoff:time - :time))
                ]
            ''')
            self.len(2, nodes)
            self.eq('visi', nodes[0].get('user'))
            self.nn(nodes[0].get('host'))
            self.nn(nodes[0].get('domain'))
            self.nn(nodes[0].get('contact'))

            self.nn(nodes[1].get('host'))
            self.nn(nodes[1].get('account'))
            self.eq(1615680000000, nodes[1].get('time'))
            self.eq(1615687260000, nodes[1].get('logoff:time'))
            self.eq(7260000, nodes[1].get('duration'))
            self.eq('02:01:00.000', nodes[1].repr('duration'))

            # Sample SIDs from here:
            # https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dtyp/81d92bba-d22b-4a8c-908a-554ab29148ab
            sids = [
                'S-1-0-0', 'S-1-1-0', 'S-1-2-0', 'S-1-2-1', 'S-1-3', 'S-1-3-0',
                'S-1-3-1', 'S-1-3-2', 'S-1-3-3', 'S-1-3-4', 'S-1-5', 'S-1-5-1',
                'S-1-5-2', 'S-1-5-3', 'S-1-5-4', 'S-1-5-6', 'S-1-5-7', 'S-1-5-8',
                'S-1-5-9', 'S-1-5-10', 'S-1-5-11', 'S-1-5-12', 'S-1-5-13', 'S-1-5-14',
                'S-1-5-15', 'S-1-5-17', 'S-1-5-18', 'S-1-5-19', 'S-1-5-20',
                'S-1-5-21-0-0-0-496', 'S-1-5-21-0-0-0-497', 'S-1-5-32-544',
                'S-1-5-32-545', 'S-1-5-32-546', 'S-1-5-32-547', 'S-1-5-32-548',
                'S-1-5-32-549', 'S-1-5-32-550', 'S-1-5-32-551', 'S-1-5-32-552',
                'S-1-5-32-554', 'S-1-5-32-555', 'S-1-5-32-556', 'S-1-5-32-557',
                'S-1-5-32-558', 'S-1-5-32-559', 'S-1-5-32-560', 'S-1-5-32-561',
                'S-1-5-32-562', 'S-1-5-32-568', 'S-1-5-32-569', 'S-1-5-32-573',
                'S-1-5-32-574', 'S-1-5-32-575', 'S-1-5-32-576', 'S-1-5-32-577',
                'S-1-5-32-578', 'S-1-5-32-579', 'S-1-5-32-580', 'S-1-5-32-582',
                'S-1-5-33', 'S-1-5-64-10', 'S-1-5-64-14', 'S-1-5-64-21', 'S-1-5-65-1',
                'S-1-5-80', 'S-1-5-80-0', 'S-1-5-83-0', 'S-1-5-84-0-0-0-0-0',
                'S-1-5-90-0', 'S-1-5-113', 'S-1-5-114', 'S-1-5-1000', 'S-1-15-2-1',
                'S-1-16-0', 'S-1-16-4096', 'S-1-16-8192', 'S-1-16-8448', 'S-1-16-12288',
                'S-1-16-16384', 'S-1-16-20480', 'S-1-16-28672', 'S-1-18-1', 'S-1-18-2',
                'S-1-18-3', 'S-1-18-4', 'S-1-18-5', 'S-1-18-6',
            ]

            opts = {'vars': {'sids': sids}}
            nodes = await core.nodes('for $sid in $sids {[ it:account=* :windows:sid=$sid ]}', opts=opts)
            self.len(88, nodes)

            nodes = await core.nodes('inet:email=visi@vertex.link -> ps:contact -> it:account -> it:logon +:time>=2021 -> it:host')
            self.len(1, nodes)
            self.eq('it:host', nodes[0].ndef[0])

            nodes = await core.nodes('it:account -> it:domain')
            self.len(1, nodes)
            self.nn(nodes[0].get('org'))
            self.eq('vertex', nodes[0].get('name'))
            self.eq('the vertex project domain', nodes[0].get('desc'))

            nodes = await core.nodes('''[
                it:log:event=*
                    :mesg=foobar
                    :data=(foo, bar, baz)
                    :severity=debug

                    :host={it:host | limit 1}
                    :sandbox:file=*
            ]''')
            self.len(1, nodes)
            self.eq(10, nodes[0].get('severity'))
            self.eq('foobar', nodes[0].get('mesg'))
            self.eq(('foo', 'bar', 'baz'), nodes[0].get('data'))
            # check that the host activity model was inherited
            self.nn(nodes[0].get('host'))
            self.len(1, await core.nodes('it:log:event :sandbox:file -> file:bytes'))

            nodes = await core.nodes('it:host | limit 1 | [ :keyboard:layout=qwerty :keyboard:language=$lib.gen.langByCode(en.us) ]')
            self.len(1, nodes)
            self.nn(nodes[0].get('keyboard:language'))
            self.len(1, await core.nodes('it:host:keyboard:layout=QWERTY'))
            self.len(1, await core.nodes('lang:language:code=en.us -> it:host'))

    async def test_it_forms_prodsoft(self):
        # Test all prodsoft and prodsoft associated linked forms
        async with self.getTestCore() as core:
            async with await core.snap() as snap:
                # it:prod:soft
                prod0 = s_common.guid()
                org0 = s_common.guid()
                person0 = s_common.guid()
                teqs = (s_common.guid(), s_common.guid())
                file0 = 'a' * 64
                acct0 = ('vertex.link', 'pennywise')
                url0 = 'https://vertex.link/products/balloonmaker'
                sprops = {
                    'name': 'Balloon Maker',
                    'type': 'hehe.haha',
                    'names': ('clowns inc',),
                    'desc': "Pennywise's patented balloon blower upper",
                    'desc:short': 'Balloon blower',
                    'author:org': org0,
                    'author:email': 'pennywise@vertex.link',
                    'author:acct': acct0,
                    'author:person': person0,
                    'techniques': teqs,
                    'url': url0,
                }
                node = await snap.addNode('it:prod:soft', prod0, sprops)
                self.eq(node.ndef[1], prod0)
                self.eq(node.get('name'), 'balloon maker')
                self.eq(node.get('desc'), "Pennywise's patented balloon blower upper")
                self.eq(node.get('desc:short'), 'balloon blower')
                self.eq(node.get('author:org'), org0)
                self.eq(node.get('author:acct'), acct0)
                self.eq(node.get('author:email'), 'pennywise@vertex.link')
                self.eq(node.get('author:person'), person0)
                self.eq(node.get('techniques'), tuple(sorted(teqs)))
                self.false(node.get('isos'))
                self.false(node.get('islib'))
                await node.set('isos', True)
                await node.set('islib', True)
                self.true(node.get('isos'))
                self.true(node.get('islib'))

                self.eq(node.get('url'), url0)

                self.len(1, await core.nodes('it:prod:soft:name="balloon maker" -> it:prod:soft:taxonomy'))
                self.len(2, await core.nodes('it:prod:softname="balloon maker" -> it:prod:soft -> it:prod:softname'))

                # it:prod:softver - this does test a bunch of property related callbacks
                url1 = 'https://vertex.link/products/balloonmaker/release_101-beta.exe'
                vprops = {
                    'vers': 'V1.0.1-beta+exp.sha.5114f85',
                    'released': '2018-04-03 08:44:22',
                    'url': url1,
                    'software': prod0,
                    'arch': 'amd64',
                    'name': 'balloonmaker',
                    'names': ('clowns inc',),
                    'desc': 'makes balloons',
                }
                ver0 = s_common.guid()
                node = await snap.addNode('it:prod:softver', ver0, vprops)

                self.eq(node.ndef[1], ver0)
                self.eq(node.get('arch'), 'amd64')
                self.eq(node.get('released'), 1522745062000)
                self.eq(node.get('software'), prod0)
                self.eq(node.get('vers'), 'V1.0.1-beta+exp.sha.5114f85')
                self.eq(node.get('vers:norm'), 'v1.0.1-beta+exp.sha.5114f85')
                self.eq(node.get('semver'), 0x000010000000001)
                self.eq(node.get('semver:major'), 1)
                self.eq(node.get('semver:minor'), 0)
                self.eq(node.get('semver:patch'), 1)
                self.eq(node.get('semver:pre'), 'beta')
                self.eq(node.get('semver:build'), 'exp.sha.5114f85')
                self.eq(node.get('url'), url1)
                self.eq(node.get('name'), 'balloonmaker')
                self.eq(node.get('desc'), 'makes balloons')
                # callback node creation checks
                nodes = await snap.nodes('it:dev:str=V1.0.1-beta+exp.sha.5114f85')
                self.len(1, nodes)
                nodes = await snap.nodes('it:dev:str=amd64')
                self.len(1, nodes)
                self.len(2, await core.nodes('it:prod:softname="balloonmaker" -> it:prod:softver -> it:prod:softname'))

                host0 = s_common.guid()
                node = await snap.addNode('it:hostsoft', (host0, ver0))
                self.eq(node.ndef[1], (host0, ver0))
                self.eq(node.get('host'), host0)
                self.eq(node.get('softver'), ver0)

                softfileprops = {'path': '/path/to/nowhere'}
                softfile = await snap.addNode('it:prod:softfile', (ver0, file0), props=softfileprops)
                self.eq(softfile.get('soft'), ver0)
                self.eq(softfile.get('file'), f'sha256:{file0}')
                self.eq('/path/to/nowhere', softfile.get('path'))
                self.len(1, await core.nodes('it:prod:softfile -> file:path'))
                nodes = await core.nodes('''
                    [ it:prod:softreg=(*, *) ]
                    { -> it:prod:softver [ :name=woot ] }
                    { -> it:dev:regval [ :key=HKEY_LOCAL_MACHINE/visi :int=31337 ] }
                ''')
                self.len(1, nodes)
                self.nn(nodes[0].get('regval'))
                self.nn(nodes[0].get('softver'))
                self.len(1, await core.nodes('it:prod:softver:name=woot -> it:prod:softreg -> it:dev:regval +:int=31337'))

                ver1 = s_common.guid()
                softlib = await snap.addNode('it:prod:softlib', (ver0, ver1))
                self.eq(softlib.get('soft'), ver0)
                self.eq(softlib.get('lib'), ver1)

                os0 = s_common.guid()
                softos = await snap.addNode('it:prod:softos', (ver0, os0))
                self.eq(softos.get('soft'), ver0)
                self.eq(softos.get('os'), os0)

                prod1 = s_common.guid()
                sigprops = {
                    'desc': 'The evil balloon virus!',
                    'url': url1,
                }
                sig0 = (prod1, 'Bar.BAZ.faZ')
                node = await snap.addNode('it:av:sig', sig0, sigprops)
                self.eq(node.ndef[1], (prod1, 'Bar.BAZ.faZ'.lower()))
                self.eq(node.get('soft'), prod1)
                self.eq(node.get('name'), 'bar.baz.faz')
                self.eq(node.get('desc'), 'The evil balloon virus!')
                self.eq(node.get('url'), url1)

                node = await snap.addNode('it:av:filehit', (file0, sig0))
                self.eq(node.ndef[1], (f'sha256:{file0}', (prod1, 'Bar.BAZ.faZ'.lower())))
                self.eq(node.get('file'), f'sha256:{file0}')
                self.eq(node.get('sig'), (prod1, 'Bar.BAZ.faZ'.lower()))
                self.eq(node.get('sig:name'), 'bar.baz.faz')
                self.eq(node.get('sig:soft'), prod1)
                await self.checkNodes(core, (('it:prod:soft', prod1),))

                self.len(1, await core.nodes('it:av:signame=bar.baz.faz -> it:av:sig'))

                # Test 'vers' semver brute forcing
                testvectors = [
                    ('1', 0x000010000000000, {'major': 1, 'minor': 0, 'patch': 0}),
                    ('2.0A1', 0x000020000000000, {'major': 2, 'minor': 0, 'patch': 0}),
                    ('2016-03-01', 0x007e00000300001, {'major': 2016, 'minor': 3, 'patch': 1}),
                    ('1.2.windows-RC1', 0x000010000200000, {'major': 1, 'minor': 2, 'patch': 0}),
                    ('3.4', 0x000030000400000, {'major': 3, 'minor': 4, 'patch': 0}),
                    ('1.3a2.dev12', 0x000010000000000, {'major': 1, 'minor': 0, 'patch': 0}),
                    ('v2.4.0.0-1', 0x000020000400000, {'major': 2, 'minor': 4, 'patch': 0}),
                    ('v2.4.1.0-0.3.rc1', 0x000020000400001, {'major': 2, 'minor': 4, 'patch': 1}),
                    ('0.18rc2', 0, {'major': 0, 'minor': 0, 'patch': 0}),
                    ('OpenSSL_1_0_2l', 0x000010000000000, {'major': 1, 'minor': 0, 'patch': 0}),
                ]
                itmod = core.getCoreMod('synapse.models.infotech.ItModule')

                for tv, te, subs in testvectors:
                    props = {
                        'vers': tv
                    }
                    node = await snap.addNode('it:prod:softver', '*', props)
                    self.eq(node.get('semver'), te)
                    self.eq(node.get('semver:major'), subs.get('major'))
                    self.eq(node.get('semver:minor'), subs.get('minor'))
                    self.eq(node.get('semver:patch'), subs.get('patch'))

                    self.eq(itmod.bruteVersionStr(tv), (te, subs))

                node = await snap.addNode('it:prod:softver', '*', {'vers': ''})
                self.eq(node.get('vers'), '')
                self.none(node.get('vers:norm'))
                self.none(node.get('semver'))

                with self.getLoggerStream('synapse.models.infotech',
                                          'Unable to parse string as a semver') as stream:

                    node = await snap.addNode('it:prod:softver', '*', {'vers': 'Alpha'})
                    self.none(node.get('semver'))
                    self.true(stream.is_set())

    async def test_it_form_callbacks(self):
        async with self.getTestCore() as core:
            async with await core.snap() as snap:
                # it:dev:str kicks out the :norm property on him when he is made
                node = await snap.addNode('it:dev:str', 'evil RAT')
                self.eq(node.ndef[1], 'evil RAT')
                self.eq(node.get('norm'), 'evil rat')

                node = await snap.addNode('it:dev:pipe', 'MyPipe')
                self.eq(node.ndef[1], 'MyPipe')
                nodes = await snap.nodes('it:dev:str=MyPipe')
                self.len(1, nodes)
                # The callback created node also has norm set on it
                self.eq(nodes[0].get('norm'), 'mypipe')

                node = await snap.addNode('it:dev:mutex', 'MyMutex')
                self.eq(node.ndef[1], 'MyMutex')
                nodes = await snap.nodes('it:dev:str=MyMutex')
                self.len(1, nodes)

                key = 'HKEY_LOCAL_MACHINE\\Foo\\Bar'
                node = await snap.addNode('it:dev:regkey', key)
                self.eq(node.ndef[1], key)
                opts = {'vars': {'key': key}}
                nodes = await snap.nodes('it:dev:str=$key', opts=opts)
                self.len(1, nodes)

                fbyts = 'sha256:' + 64 * 'f'
                key = 'HKEY_LOCAL_MACHINE\\DUCK\\QUACK'
                valus = [
                    ('str', 'knight'),
                    ('int', 20),
                    ('bytes', fbyts),
                ]
                for prop, valu in valus:

                    iden = s_common.guid((key, valu))
                    props = {
                        'key': key,
                        prop: valu,
                    }
                    node = await snap.addNode('it:dev:regval', iden, props)
                    self.eq(node.ndef[1], iden)
                    self.eq(node.get('key'), key)
                    self.eq(node.get(prop), valu)

                nodes = await snap.nodes('it:dev:str=HKEY_LOCAL_MACHINE\\Foo\\Bar')
                self.len(1, nodes)

    async def test_it_semvertype(self):
        async with self.getTestCore() as core:
            t = core.model.type('it:semver')
            testvectors = (
                # Strings
                ('1.2.3', (0x000010000200003,
                           {'major': 1, 'minor': 2, 'patch': 3, })),
                ('0.0.1', (0x000000000000001,
                           {'major': 0, 'minor': 0, 'patch': 1, })),
                ('1.2.3-alpha', (0x000010000200003,
                                 {'major': 1, 'minor': 2, 'patch': 3,
                                  'pre': 'alpha', })),
                ('1.2.3-alpha.1', (0x000010000200003,
                                   {'major': 1, 'minor': 2, 'patch': 3,
                                    'pre': 'alpha.1', })),
                ('1.2.3-0.3.7', (0x000010000200003,
                                 {'major': 1, 'minor': 2, 'patch': 3,
                                  'pre': '0.3.7', })),
                ('1.2.3-x.7.z.92', (0x000010000200003,
                                    {'major': 1, 'minor': 2, 'patch': 3,
                                     'pre': 'x.7.z.92', })),
                ('1.2.3-alpha+001', (0x000010000200003,
                                     {'major': 1, 'minor': 2, 'patch': 3,
                                      'pre': 'alpha', 'build': '001'})),
                ('1.2.3+20130313144700', (0x000010000200003,
                                          {'major': 1, 'minor': 2, 'patch': 3,
                                           'build': '20130313144700'})),
                ('1.2.3-beta+exp.sha.5114f85', (0x000010000200003,
                                                {'major': 1, 'minor': 2, 'patch': 3,
                                                 'pre': 'beta',
                                                 'build': 'exp.sha.5114f85'})),
                # Real world examples
                ('1.2.3-B5CD5743F', (0x000010000200003,
                                     {'major': 1, 'minor': 2, 'patch': 3,
                                      'pre': 'B5CD5743F', })),
                ('V1.2.3', (0x000010000200003,
                            {'major': 1, 'minor': 2, 'patch': 3, })),
                ('V1.4.0-RC0', (0x000010000400000,
                                {'major': 1, 'minor': 4, 'patch': 0,
                                 'pre': 'RC0', })),
                ('v2.4.1-0.3.rc1', (0x000020000400001,
                                    {'major': 2, 'minor': 4, 'patch': 1,
                                     'pre': '0.3.rc1'})),
                ('0.18.1', (0x000000001200001,
                            {'major': 0, 'minor': 18, 'patch': 1, })),
                # Integer values
                (0, (0, {'major': 0, 'minor': 0, 'patch': 0})),
                (1, (1, {'major': 0, 'minor': 0, 'patch': 1})),
                (2, (2, {'major': 0, 'minor': 0, 'patch': 2})),
                (0xFFFFF, (0xFFFFF, {'major': 0, 'minor': 0, 'patch': 0xFFFFF})),
                (0xFFFFF + 1, (0xFFFFF + 1, {'major': 0, 'minor': 1, 'patch': 0})),
                (0xdeadb33f1337133, (0xdeadb33f1337133, {'major': 0xdeadb, 'minor': 0x33f13, 'patch': 0x37133})),
                (0xFFFFFFFFFFFFFFF, (0xFFFFFFFFFFFFFFF, {'major': 0xFFFFF, 'minor': 0xFFFFF, 'patch': 0xFFFFF})),
                # Brute forced strings
                ('1', (1099511627776, {'major': 1, 'minor': 0, 'patch': 0})),
                ('1.2', (1099513724928, {'major': 1, 'minor': 2, 'patch': 0})),
                ('2.0A1', (2199023255552, {'major': 2, 'minor': 0, 'patch': 0})),
                ('0.18rc2', (0, {'major': 0, 'minor': 0, 'patch': 0})),
                ('0.0.00001', (1, {'major': 0, 'minor': 0, 'patch': 1})),
                ('2016-03-01', (2216615444742145, {'major': 2016, 'minor': 3, 'patch': 1})),
                ('v2.4.0.0-1', (2199027449856, {'major': 2, 'minor': 4, 'patch': 0})),
                ('1.3a2.dev12', (1099511627776, {'major': 1, 'minor': 0, 'patch': 0})),
                ('OpenSSL_1_0_2l', (1099511627776, {'major': 1, 'minor': 0, 'patch': 0})),
                ('1.2.windows-RC1', (1099513724928, {'major': 1, 'minor': 2, 'patch': 0})),
                ('v2.4.1.0-0.3.rc1', (2199027449857, {'major': 2, 'minor': 4, 'patch': 1})),
                ('1.2.3-alpha.foo..+001', (1099513724931, {'major': 1, 'minor': 2, 'patch': 3})),
                ('1.2.3-alpha.foo.001+001', (1099513724931, {'major': 1, 'minor': 2, 'patch': 3})),
                ('1.2.3-alpha+001.blahblahblah...', (1099513724931, {'major': 1, 'minor': 2, 'patch': 3})),
                ('1.2.3-alpha+001.blahblahblah.*iggy', (1099513724931, {'major': 1, 'minor': 2, 'patch': 3}))
            )

            for v, e in testvectors:
                ev, es = e
                valu, rdict = t.norm(v)
                subs = rdict.get('subs')
                self.eq(valu, ev)
                self.eq(subs, es)

            testvectors_bad = (
                # invalid ints
                -1,
                0xFFFFFFFFFFFFFFFFFFFFFFFF + 1,
                # Just bad input
                '   ',
                ' alpha ',
            )
            for v in testvectors_bad:
                self.raises(s_exc.BadTypeValu, t.norm, v)

            testvectors_repr = (
                (0, '0.0.0'),
                (1, '0.0.1'),
                (0x000010000200003, '1.2.3'),
            )
            for v, e in testvectors_repr:
                self.eq(t.repr(v), e)

    async def test_it_forms_screenshot(self):
        async with self.getTestCore() as core:
            nodes = await core.nodes('''[
                it:screenshot=*
                    :host=*
                    :image=*
                    :desc=WootWoot
                    :sandbox:file=*
            ]''')

            self.len(1, nodes)
            self.eq('it:screenshot', nodes[0].ndef[0])
            self.eq('WootWoot', nodes[0].props['desc'])

            self.len(1, await core.nodes('it:screenshot :host -> it:host'))
            self.len(1, await core.nodes('it:screenshot :image -> file:bytes'))
            self.len(1, await core.nodes('it:screenshot :sandbox:file -> file:bytes'))

    async def test_it_forms_hardware(self):
        async with self.getTestCore() as core:
            nodes = await core.nodes('''[
                it:prod:hardware=*
                    :make=dell
                    :model=XPS13
                    :version=alpha
                    :type=pc.laptop
                    :desc=WootWoot
                    :released=20220202
                    :cpe=cpe:2.3:h:dell:xps13::::::::
                    :parts = (*, *)
            ]''')
            self.eq('WootWoot', nodes[0].props['desc'])
            self.eq('dell', nodes[0].props['make'])
            self.eq('xps13', nodes[0].props['model'])
            self.eq('alpha', nodes[0].props['version'])
            self.eq('cpe:2.3:h:dell:xps13::::::::', nodes[0].props['cpe'])
            self.eq(1643760000000, nodes[0].props['released'])
            self.len(1, await core.nodes('it:prod:hardware :make -> ou:name'))
            self.len(1, await core.nodes('it:prod:hardware :type -> it:prod:hardwaretype'))
            self.len(2, await core.nodes('it:prod:hardware:make=dell -> it:prod:hardware'))

            nodes = await core.nodes('''[
                it:prod:component=*
                    :hardware={it:prod:hardware:make=dell}
                    :serial=asdf1234
                    :host=*
            ]''')
            self.nn(nodes[0].props['host'])
            self.eq('asdf1234', nodes[0].props['serial'])
            self.len(1, await core.nodes('it:prod:component -> it:host'))
            self.len(1, await core.nodes('it:prod:component -> it:prod:hardware +:make=dell'))

    async def test_it_forms_hostexec(self):
        # forms related to the host execution model
        async with self.getTestCore() as core:
            async with await core.snap() as snap:
                exe = 'sha256:' + 'a' * 64
                port = 80
                tick = s_common.now()
                host = s_common.guid()
                proc = s_common.guid()
                mutex = 'giggleXX_X0'
                pipe = 'pipe\\mynamedpipe'
                user = 'serviceadmin'
                pid = 20
                key = 'HKEY_LOCAL_MACHINE\\Foo\\Bar'
                ipv4 = 0x01020304
                ipv6 = '::1'

                sandfile = 'sha256:' + 'b' * 64
                addr4 = f'tcp://1.2.3.4:{port}'
                addr6 = f'udp://[::1]:{port}'
                url = 'http://www.google.com/sekrit.html'
                raw_path = r'c:\Windows\System32\rar.exe'
                norm_path = r'c:/windows/system32/rar.exe'
                src_proc = s_common.guid()
                src_path = r'c:/temp/ping.exe'
                cmd0 = 'rar a -r yourfiles.rar *.txt'
                fpath = 'c:/temp/yourfiles.rar'
                fbyts = 'sha256:' + 'b' * 64
                pprops = {
                    'exe': exe,
                    'pid': pid,
                    'cmd': cmd0,
                    'host': host,
                    'time': tick,
                    'user': user,
                    'account': '*',
                    'path': raw_path,
                    'src:exe': src_path,
                    'src:proc': src_proc,
                    'sandbox:file': sandfile,
                }
                node = await snap.addNode('it:exec:proc', proc, pprops)
                self.eq(node.ndef[1], proc)
                self.eq(node.get('exe'), exe)
                self.eq(node.get('pid'), pid)
                self.eq(node.get('cmd'), cmd0)
                self.eq(node.get('host'), host)
                self.eq(node.get('time'), tick)
                self.eq(node.get('user'), user)
                self.eq(node.get('path'), norm_path)
                self.eq(node.get('src:exe'), src_path)
                self.eq(node.get('src:proc'), src_proc)
                self.eq(node.get('sandbox:file'), sandfile)

                self.nn(node.get('account'))
                self.len(1, await core.nodes('it:exec:proc -> it:account'))

                nodes = await core.nodes('it:cmd')
                self.len(1, nodes)
                self.eq(nodes[0].ndef, ('it:cmd', 'rar a -r yourfiles.rar *.txt'))

                m0 = s_common.guid()
                mprops = {
                    'exe': exe,
                    'proc': proc,
                    'name': mutex,
                    'host': host,
                    'time': tick,
                    'sandbox:file': sandfile,
                }
                node = await snap.addNode('it:exec:mutex', m0, mprops)
                self.eq(node.ndef[1], m0)
                self.eq(node.get('exe'), exe)
                self.eq(node.get('proc'), proc)
                self.eq(node.get('host'), host)
                self.eq(node.get('time'), tick)
                self.eq(node.get('name'), mutex)
                self.eq(node.get('sandbox:file'), sandfile)

                p0 = s_common.guid()
                pipeprops = {
                    'exe': exe,
                    'proc': proc,
                    'name': pipe,
                    'host': host,
                    'time': tick,
                    'sandbox:file': sandfile,
                }
                node = await snap.addNode('it:exec:pipe', p0, pipeprops)
                self.eq(node.ndef[1], p0)
                self.eq(node.get('exe'), exe)
                self.eq(node.get('proc'), proc)
                self.eq(node.get('host'), host)
                self.eq(node.get('time'), tick)
                self.eq(node.get('name'), pipe)
                self.eq(node.get('sandbox:file'), sandfile)

                u0 = s_common.guid()
                uprops = {
                    'proc': proc,
                    'host': host,
                    'exe': exe,
                    'time': tick,
                    'url': url,
                    'page:pdf': '*',
                    'page:html': '*',
                    'page:image': '*',
                    'browser': '*',
                    'client': addr4,
                    'sandbox:file': sandfile,
                }
                node = await snap.addNode('it:exec:url', u0, uprops)
                self.eq(node.ndef[1], u0)
                self.eq(node.get('exe'), exe)
                self.eq(node.get('proc'), proc)
                self.eq(node.get('host'), host)
                self.eq(node.get('time'), tick)
                self.eq(node.get('url'), url)
                self.eq(node.get('client'), addr4)
                self.eq(node.get('client:ipv4'), ipv4)
                self.eq(node.get('client:port'), port)
                self.eq(node.get('sandbox:file'), sandfile)

                self.nn(node.get('page:pdf'))
                self.nn(node.get('page:html'))
                self.nn(node.get('page:image'))
                self.nn(node.get('browser'))
                opts = {'vars': {'guid': u0}}
                self.len(1, await core.nodes('it:exec:url=$guid :page:pdf -> file:bytes', opts=opts))
                self.len(1, await core.nodes('it:exec:url=$guid :page:html -> file:bytes', opts=opts))
                self.len(1, await core.nodes('it:exec:url=$guid :page:image -> file:bytes', opts=opts))
                self.len(1, await core.nodes('it:exec:url=$guid :browser -> it:prod:softver', opts=opts))
                self.len(1, await core.nodes('it:exec:url=$guid :sandbox:file -> file:bytes', opts=opts))

                u1 = s_common.guid()
                uprops['client'] = addr6
                node = await snap.addNode('it:exec:url', u1, uprops)
                self.eq(node.ndef[1], u1)
                self.eq(node.get('client'), addr6)
                self.eq(node.get('client:ipv6'), ipv6)
                self.eq(node.get('client:port'), port)

                b0 = s_common.guid()
                bprops = {
                    'proc': proc,
                    'host': host,
                    'exe': exe,
                    'time': tick,
                    'server': addr4,
                    'sandbox:file': sandfile,
                }
                node = await snap.addNode('it:exec:bind', b0, bprops)
                self.eq(node.ndef[1], b0)
                self.eq(node.get('exe'), exe)
                self.eq(node.get('proc'), proc)
                self.eq(node.get('host'), host)
                self.eq(node.get('time'), tick)
                self.eq(node.get('server'), addr4)
                self.eq(node.get('server:ipv4'), ipv4)
                self.eq(node.get('server:port'), port)
                self.eq(node.get('sandbox:file'), sandfile)

                b1 = s_common.guid()
                bprops['server'] = addr6
                node = await snap.addNode('it:exec:bind', b1, bprops)
                self.eq(node.ndef[1], b1)
                self.eq(node.get('server'), addr6)
                self.eq(node.get('server:ipv6'), ipv6)
                self.eq(node.get('server:port'), port)

                faprops = {
                    'exe': exe,
                    'host': host,
                    'proc': proc,
                    'file': fbyts,
                    'time': tick,
                    'path': fpath,
                    'sandbox:file': sandfile,
                }
                fa0 = s_common.guid()
                node = await snap.addNode('it:exec:file:add', fa0, faprops)
                self.eq(node.ndef[1], fa0)
                self.eq(node.get('exe'), exe)
                self.eq(node.get('host'), host)
                self.eq(node.get('proc'), proc)
                self.eq(node.get('time'), tick)
                self.eq(node.get('file'), fbyts)
                self.eq(node.get('path'), fpath)
                self.eq(node.get('path:dir'), 'c:/temp')
                self.eq(node.get('path:base'), 'yourfiles.rar')
                self.eq(node.get('path:ext'), 'rar')
                self.eq(node.get('sandbox:file'), sandfile)

                fr0 = s_common.guid()
                node = await snap.addNode('it:exec:file:read', fr0, faprops)
                self.eq(node.ndef[1], fr0)
                self.eq(node.get('exe'), exe)
                self.eq(node.get('host'), host)
                self.eq(node.get('proc'), proc)
                self.eq(node.get('time'), tick)
                self.eq(node.get('file'), fbyts)
                self.eq(node.get('path'), fpath)
                self.eq(node.get('path:dir'), 'c:/temp')
                self.eq(node.get('path:base'), 'yourfiles.rar')
                self.eq(node.get('path:ext'), 'rar')
                self.eq(node.get('sandbox:file'), sandfile)

                fw0 = s_common.guid()
                node = await snap.addNode('it:exec:file:write', fw0, faprops)
                self.eq(node.ndef[1], fw0)
                self.eq(node.get('exe'), exe)
                self.eq(node.get('host'), host)
                self.eq(node.get('proc'), proc)
                self.eq(node.get('time'), tick)
                self.eq(node.get('file'), fbyts)
                self.eq(node.get('path'), fpath)
                self.eq(node.get('path:dir'), 'c:/temp')
                self.eq(node.get('path:base'), 'yourfiles.rar')
                self.eq(node.get('path:ext'), 'rar')
                self.eq(node.get('sandbox:file'), sandfile)

                fd0 = s_common.guid()
                node = await snap.addNode('it:exec:file:del', fd0, faprops)
                self.eq(node.ndef[1], fd0)
                self.eq(node.get('exe'), exe)
                self.eq(node.get('host'), host)
                self.eq(node.get('proc'), proc)
                self.eq(node.get('time'), tick)
                self.eq(node.get('file'), fbyts)
                self.eq(node.get('path'), fpath)
                self.eq(node.get('path:dir'), 'c:/temp')
                self.eq(node.get('path:base'), 'yourfiles.rar')
                self.eq(node.get('path:ext'), 'rar')
                self.eq(node.get('sandbox:file'), sandfile)

                file0 = s_common.guid()
                fsprops = {
                    'host': host,
                    'path': fpath,
                    'file': fbyts,
                    'ctime': tick,
                    'mtime': tick + 1,
                    'atime': tick + 2,
                    'user': user,
                    'group': 'domainadmin'
                }
                node = await snap.addNode('it:fs:file', file0, fsprops)
                self.eq(node.ndef[1], file0)
                self.eq(node.get('host'), host)
                self.eq(node.get('user'), user)
                self.eq(node.get('group'), 'domainadmin')
                self.eq(node.get('file'), fbyts)
                self.eq(node.get('ctime'), tick)
                self.eq(node.get('mtime'), tick + 1)
                self.eq(node.get('atime'), tick + 2)
                self.eq(node.get('path'), fpath)
                self.eq(node.get('path:dir'), 'c:/temp')
                self.eq(node.get('path:base'), 'yourfiles.rar')
                self.eq(node.get('path:ext'), 'rar')

                rprops = {
                    'host': host,
                    'proc': proc,
                    'exe': exe,
                    'time': tick,
                    'reg': '*',
                    'sandbox:file': sandfile,
                }
                forms = ('it:exec:reg:get',
                         'it:exec:reg:set',
                         'it:exec:reg:del',
                         )
                for form in forms:
                    rk0 = s_common.guid()
                    nprops = rprops.copy()
                    node = await snap.addNode(form, rk0, nprops)
                    self.eq(node.ndef[1], rk0)
                    self.eq(node.get('host'), host)
                    self.eq(node.get('proc'), proc)
                    self.eq(node.get('exe'), exe)
                    self.eq(node.get('time'), tick)
                    self.nn(node.get('reg'))
                    self.eq(node.get('sandbox:file'), sandfile)

    async def test_it_app_yara(self):

        async with self.getTestCore() as core:

            rule = s_common.guid()
            opts = {'vars': {'rule': rule}}

            nodes = await core.nodes('''
                [ it:app:yara:rule=$rule
                    :ext:id=V-31337
                    :url=https://vertex.link/yara-lolz/V-31337
                    :family=Beacon
                    :created=20200202 :updated=20220401
                    :enabled=true :text=gronk :author=* :name=foo :version=1.2.3 ]
            ''', opts=opts)

            self.len(1, nodes)
            self.eq('foo', nodes[0].get('name'))
            self.eq('V-31337', nodes[0].get('ext:id'))
            self.eq('https://vertex.link/yara-lolz/V-31337', nodes[0].get('url'))
            self.eq(True, nodes[0].get('enabled'))
            self.eq(1580601600000, nodes[0].get('created'))
            self.eq(1648771200000, nodes[0].get('updated'))
            self.eq('gronk', nodes[0].get('text'))
            self.eq('beacon', nodes[0].get('family'))
            self.eq(0x10000200003, nodes[0].get('version'))

            self.len(1, await core.nodes('it:app:yara:rule=$rule -> ps:contact', opts=opts))

            nodes = await core.nodes('[ it:app:yara:match=($rule, "*") :version=1.2.3 ]', opts=opts)
            self.len(1, nodes)
            self.nn(nodes[0].get('file'))
            self.eq(rule, nodes[0].get('rule'))
            self.eq(0x10000200003, nodes[0].get('version'))

    async def test_it_app_snort(self):

        async with self.getTestCore() as core:

            hit = s_common.guid()
            rule = s_common.guid()
            flow = s_common.guid()
            host = s_common.guid()
            opts = {'vars': {'rule': rule, 'flow': flow, 'host': host, 'hit': hit}}

            nodes = await core.nodes('''
            [ it:app:snort:rule=$rule
                :id=999
                :engine=1
                :text=gronk
                :name=foo
                :author = {[ ps:contact=* :name=visi ]}
                :created = 20120101
                :updated = 20220101
                :enabled=1
                :family=redtree
                :version=1.2.3 ]
            ''', opts=opts)

            self.len(1, nodes)
            self.eq('999', nodes[0].get('id'))
            self.eq(1, nodes[0].get('engine'))
            self.eq('foo', nodes[0].get('name'))
            self.eq('gronk', nodes[0].get('text'))
            self.eq('redtree', nodes[0].get('family'))
            self.eq(True, nodes[0].get('enabled'))
            self.eq(0x10000200003, nodes[0].get('version'))
            self.eq(1325376000000, nodes[0].get('created'))
            self.eq(1640995200000, nodes[0].get('updated'))
            self.nn(nodes[0].get('author'))

            nodes = await core.nodes('[ it:app:snort:hit=$hit :rule=$rule :flow=$flow :src="tcp://[::ffff:0102:0304]:0" :dst="tcp://[::ffff:0505:0505]:80" :time=2015 :sensor=$host :version=1.2.3 ]', opts=opts)
            self.len(1, nodes)
            self.eq(rule, nodes[0].get('rule'))
            self.eq(flow, nodes[0].get('flow'))
            self.eq(host, nodes[0].get('sensor'))
            self.eq(1420070400000, nodes[0].get('time'))

            self.eq('tcp://[::ffff:1.2.3.4]:0', nodes[0].get('src'))
            self.eq(0, nodes[0].get('src:port'))
            self.eq(0x01020304, nodes[0].get('src:ipv4'))
            self.eq('::ffff:1.2.3.4', nodes[0].get('src:ipv6'))

            self.eq('tcp://[::ffff:5.5.5.5]:80', nodes[0].get('dst'))
            self.eq(80, nodes[0].get('dst:port'))
            self.eq(0x05050505, nodes[0].get('dst:ipv4'))
            self.eq('::ffff:5.5.5.5', nodes[0].get('dst:ipv6'))

            self.eq(0x10000200003, nodes[0].get('version'))

    async def test_it_reveng(self):

        async with self.getTestCore() as core:

            baseFile = s_common.ehex(s_common.buid())
            func = s_common.guid()
            fva = 0x404438
            rank = 33
            complexity = 60
            funccalls = ((baseFile, func), )
            fopt = {'vars': {'file': baseFile,
                             'func': func,
                             'fva': fva,
                             'rank': rank,
                             'cmplx': complexity,
                             'funccalls': funccalls}}
            vstr = 'VertexBrandArtisanalBinaries'
            sopt = {'vars': {'func': func,
                             'string': vstr}}
            name = "FunkyFunction"
            descrp = "Test Function"
            impcalls = ("libr.foo", "libr.foo2", "libr.foo3")
            funcopt = {'vars': {'name': name,
                                'descrp': descrp,
                                'impcalls': impcalls}}

            fnode = await core.nodes('[it:reveng:filefunc=($file, $func) :va=$fva :rank=$rank :complexity=$cmplx :funccalls=$funccalls]', opts=fopt)
            snode = await core.nodes('[it:reveng:funcstr=($func, $string)]', opts=sopt)
            self.len(1, fnode)
            self.eq(f'sha256:{baseFile}', fnode[0].get('file'))
            self.eq(fva, fnode[0].get('va'))
            self.eq(rank, fnode[0].get('rank'))
            self.eq(complexity, fnode[0].get('complexity'))
            self.eq((f'sha256:{baseFile}', func), fnode[0].get('funccalls')[0])

            self.len(1, snode)
            self.eq(fnode[0].get('function'), snode[0].get('function'))
            self.eq(vstr, snode[0].get('string'))

            funcnode = await core.nodes('''
                it:reveng:function [
                    :name=$name
                    :description=$descrp
                    :impcalls=$impcalls
                    :strings=(bar,foo,foo)
            ]''', opts=funcopt)
            self.len(1, funcnode)
            self.eq(name, funcnode[0].get('name'))
            self.eq(descrp, funcnode[0].get('description'))
            self.len(len(impcalls), funcnode[0].get('impcalls'))
            self.eq(impcalls[0], funcnode[0].get('impcalls')[0])
            self.sorteq(('bar', 'foo'), funcnode[0].get('strings'))

            nodes = await core.nodes('it:reveng:function -> it:dev:str')
            self.len(2, nodes)

            nodes = await core.nodes(f'file:bytes={baseFile} -> it:reveng:filefunc :function -> it:reveng:funcstr:function')
            self.len(1, nodes)
            self.eq(vstr, nodes[0].get('string'))

            nodes = await core.nodes(f'file:bytes={baseFile} -> it:reveng:filefunc -> it:reveng:function -> it:reveng:impfunc')
            self.len(len(impcalls), nodes)

    async def test_infotech_cpes(self):

        async with self.getTestCore() as core:

            cpe23 = core.model.type('it:sec:cpe')
            cpe22 = core.model.type('it:sec:cpe:v2_2')

            with self.raises(s_exc.BadTypeValu):
                cpe22.norm('cpe:/a:vertex:synapse:0:1:2:3:4:5:6:7:8:9')

            with self.raises(s_exc.BadTypeValu):
                cpe23.norm('cpe:/a:vertex:synapse:0:1:2:3:4:5:6:7:8:9')

            # test cast 2.2 -> 2.3 upsample
            norm, info = cpe23.norm('cpe:/a:vertex:synapse')
            self.eq(norm, 'cpe:2.3:a:vertex:synapse:*:*:*:*:*:*:*:*')

            # test cast 2.3 -> 2.2 downsample
            norm, info = cpe22.norm('cpe:2.3:a:vertex:synapse:*:*:*:*:*:*:*:*')
            self.eq(norm, 'cpe:/a:vertex:synapse')

            nodes = await core.nodes('[ it:sec:cpe=cpe:2.3:a:vertex:synapse:*:*:*:*:*:*:*:* ]')
            self.eq('cpe:/a:vertex:synapse', nodes[0].props['v2_2'])

            # test lift by either via upsample and downsample
            self.len(1, await core.nodes('it:sec:cpe=cpe:/a:vertex:synapse +:v2_2=cpe:/a:vertex:synapse'))
            self.len(1, await core.nodes('it:sec:cpe=cpe:2.3:a:vertex:synapse:*:*:*:*:*:*:*:*'))
            self.len(1, await core.nodes('it:sec:cpe:v2_2=cpe:/a:vertex:synapse'))
            self.len(1, await core.nodes('it:sec:cpe:v2_2=cpe:2.3:a:vertex:synapse:*:*:*:*:*:*:*:*'))

    async def test_infotech_c2config(self):
        async with self.getTestCore() as core:
            nodes = await core.nodes('''
                [ it:sec:c2:config=*
                    :file=*
                    :family=Beacon
                    :servers=(http://1.2.3.4, tcp://visi:secret@vertex.link)
                    :decoys=(https://woot.com, https://foo.bar)
                    :listens=(https://0.0.0.0:443,)
                    :proxies=(socks5://visi:secret@1.2.3.4:1234,)
                    :dns:resolvers=(udp://8.8.8.8:53,)
                    :http:headers=(
                        (user-agent, wootbot),
                    )
                    :mutex=OnlyOnce
                    :crypto:key=*
                    :campaigncode=WootWoot
                    :raw = ({"hehe": "haha"})
                    :connect:delay=01:00:00
                    :connect:interval=08:00:00
                ]
            ''')
            node = nodes[0]
            self.nn(node.get('file'))
            self.nn(node.get('crypto:key'))
            self.eq('OnlyOnce', node.get('mutex'))
            self.eq('beacon', node.get('family'))
            self.eq('WootWoot', node.get('campaigncode'))
            self.eq(('http://1.2.3.4', 'tcp://visi:secret@vertex.link'), node.get('servers'))
            self.eq(3600000, node.get('connect:delay'))
            self.eq(28800000, node.get('connect:interval'))
            self.eq({'hehe': 'haha'}, node.get('raw'))
            self.eq(('https://0.0.0.0:443',), node.get('listens'))
            self.eq(('socks5://visi:secret@1.2.3.4:1234',), node.get('proxies'))
            self.eq(('udp://8.8.8.8:53',), node.get('dns:resolvers'))
            self.eq(('https://woot.com', 'https://foo.bar',), node.get('decoys'))

    async def test_infotech_query(self):

        async with self.getTestCore() as core:

            nodes = await core.nodes('''
                [ it:exec:query=*
                    :text="SELECT * FROM threats"
                    :language="SQL"
                    :opts=({"foo": "bar"})
                    :api:url=https://vertex.link/api/v1.
                    :time=20220720
                    :offset=99
                    // we can assume the rest of the interface props work
                ]
            ''')
            self.eq(1658275200000, nodes[0].get('time'))
            self.eq(99, nodes[0].get('offset'))
            self.eq('sql', nodes[0].get('language'))
            self.eq({"foo": "bar"}, nodes[0].get('opts'))
            self.eq('SELECT * FROM threats', nodes[0].get('text'))
            self.len(1, await core.nodes('it:exec:query -> it:query +it:query="SELECT * FROM threats"'))

    async def test_infotech_softid(self):

        async with self.getTestCore() as core:

            nodes = await core.nodes('''
                [ it:prod:softid=*
                    :id=Woot
                    :host=*
                    :soft={[ it:prod:softver=* :name=beacon ]}
                    :soft:name=beacon
                ]
            ''')
            self.len(1, nodes)
            self.eq('Woot', nodes[0].get('id'))
            self.nn(nodes[0].get('host'))
            self.nn(nodes[0].get('soft'))
            self.len(1, await core.nodes('it:host -> it:prod:softid'))
            self.len(1, await core.nodes('it:prod:softver:name=beacon -> it:prod:softid'))

    async def test_infotech_repo(self):

        async with self.getTestCore() as core:
            diff = s_common.guid()
            repo = s_common.guid()
            issue = s_common.guid()
            commit = s_common.guid()
            branch = s_common.guid()
            icom = s_common.guid()
            dcom = s_common.guid()
            origin = s_common.guid()
            label = s_common.guid()
            issuelabel = s_common.guid()
            file = f"sha256:{hashlib.sha256(b'foobarbaz').hexdigest()}"

            props = {
                ('it:dev:repo', repo): {
                    'name': 'synapse',
                    'desc': 'Synapse Central Intelligence System',
                    'created': 0,
                    'url': 'https://github.com/vertexproject/synapse',
                    'type': 'svn.',
                    'submodules': (s_common.guid(),),
                },

                ('it:dev:repo:remote', s_common.guid()): {
                    'name': 'origin',
                    'repo': repo,
                    'url': 'git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/staging',
                    'remote': origin,
                },

                ('it:dev:repo:commit', commit): {
                    'repo': repo,
                    'branch': branch,
                    'parents': (s_common.guid(),),
                    'mesg': 'fancy new release',
                    'id': 'r12345',
                    'created': 0,
                    'url': 'https://github.com/vertexproject/synapse/commit/03c71e723bceedb38ef8fc14543c30b9e82e64cf',
                },

                ('it:dev:repo:diff', diff): {
                    'commit': commit,
                    'file': file,
                    'path': 'synapse/tests/test_model_infotech.py',
                    'url': 'https://github.com/vertexproject/synapse/compare/it_dev_repo_models?expand=1',
                },

                ('it:dev:repo:issue', issue): {
                    'repo': repo,
                    'title': 'a fancy new release',
                    'desc': 'Gonna be a big release friday',
                    'created': 1,
                    'updated': 1,
                    'id': '1234',
                    'url': 'https://github.com/vertexproject/synapse/issues/2821',
                },

                ('it:dev:repo:label', label): {
                    'id': '123456789',
                    'title': 'new feature',
                    'desc': 'a super cool new feature'
                },

                ('it:dev:repo:issue:label', issuelabel): {
                    'issue': issue,
                    'label': label,
                    'applied': 97,
                    'removed': 98
                },

                ('it:dev:repo:issue:comment', icom): {
                    'issue': issue,
                    'text': 'a comment on an issue',
                    'replyto': s_common.guid(),
                    'url': 'https://github.com/vertexproject/synapse/issues/2821#issuecomment-1557053758',
                    'created': 12,
                    'updated': 93
                },

                ('it:dev:repo:diff:comment', dcom): {
                    'diff': diff,
                    'text': 'types types types types types',
                    'replyto': s_common.guid(),
                    'line': 100,
                    'offset': 100,
                    'url': 'https://github.com/vertexproject/synapse/pull/3257#discussion_r1273368069',
                    'created': 1,
                    'updated': 3
                },

                ('it:dev:repo:branch', branch): {
                    'parent': s_common.guid(),
                    'start': commit,
                    'name': 'IT_dev_repo_models',
                    'url': 'https://github.com/vertexproject/synapse/tree/it_dev_repo_models',
                    'created': 0,
                    'merged': 1,
                    'deleted': 2
                }
            }

            async with await core.snap() as snap:
                for (form, valu), props in props.items():
                    node = await snap.addNode(form, valu, props=props)
                    self.checkNode(node, ((form, valu), props))

            nodes = await core.nodes('it:dev:repo')
            self.len(2, nodes)

            nodes = await core.nodes('it:dev:repo <- *')
            self.len(4, nodes)

            nodes = await core.nodes('it:dev:repo:commit')
            self.len(3, nodes)

            nodes = await core.nodes('it:dev:repo:type:taxonomy')
            self.len(1, nodes)

            nodes = await core.nodes('it:dev:repo:issue:comment')
            self.len(2, nodes)

            nodes = await core.nodes('it:dev:repo:diff:comment')
            self.len(2, nodes)

            nodes = await core.nodes('it:dev:repo:remote')
            self.len(1, nodes)

            nodes = await core.nodes('it:dev:repo:remote :repo -> it:dev:repo')
            self.len(1, nodes)
            self.eq(nodes[0].ndef, ('it:dev:repo', repo))

            nodes = await core.nodes('it:dev:repo:remote :remote -> it:dev:repo')
            self.len(1, nodes)
            self.eq(nodes[0].ndef, ('it:dev:repo', origin))

            nodes = await core.nodes('it:dev:repo:issue:comment=$guid :replyto -> *', {'vars': {'guid': icom}})
            self.len(1, nodes)

            nodes = await core.nodes('it:dev:repo:diff:comment=$guid :replyto -> *', {'vars': {'guid': dcom}})
            self.len(1, nodes)

            nodes = await core.nodes('it:dev:repo:branch=$guid :parent -> *', {'vars': {'guid': branch}})
            self.len(1, nodes)

    async def test_infotech_vulnscan(self):

        async with self.getTestCore() as core:
            nodes = await core.nodes('''
                [ it:sec:vuln:scan=*
                    :time=202308180819
                    :desc="Woot Woot"
                    :ext:id=FOO-10
                    :ext:url=https://vertex.link/scans/FOO-10
                    :software:name=nessus
                    :software={[ it:prod:softver=* :name=nessus ]}
                    :operator={[ ps:contact=* :name=visi ]}
                ]
            ''')
            self.len(1, nodes)

            self.eq(1692346740000, nodes[0].get('time'))
            self.eq('nessus', nodes[0].get('software:name'))
            self.eq('Woot Woot', nodes[0].get('desc'))
            self.eq('FOO-10', nodes[0].get('ext:id'))
            self.eq('https://vertex.link/scans/FOO-10', nodes[0].get('ext:url'))

            self.nn(nodes[0].get('operator'))
            self.nn(nodes[0].get('software'))

            self.len(1, await core.nodes('it:sec:vuln:scan -> ps:contact +:name=visi'))
            self.len(1, await core.nodes('it:sec:vuln:scan -> it:prod:softver +:name=nessus'))

            nodes = await core.nodes('''
                [ it:sec:vuln:scan:result=*
                    :scan={it:sec:vuln:scan}
                    :vuln={[ risk:vuln=* :name="nucsploit9k" ]}
                    :desc="Network service is vulnerable to nucsploit9k"
                    :ext:id=FOO-10.0
                    :ext:url=https://vertex.link/scans/FOO-10/0
                    :time=2023081808190828
                    :mitigated=2023081808190930
                    :mitigation={[ risk:mitigation=* :name="mitigate this" ]}
                    :asset=(inet:server, tcp://1.2.3.4:443)
                    :priority=high
                    :severity=highest
                ]
            ''')
            self.len(1, nodes)
            self.eq(40, nodes[0].get('priority'))
            self.eq(50, nodes[0].get('severity'))
            self.eq(1692346748280, nodes[0].get('time'))
            self.eq(1692346749300, nodes[0].get('mitigated'))
            self.eq('Network service is vulnerable to nucsploit9k', nodes[0].get('desc'))
            self.eq('FOO-10.0', nodes[0].get('ext:id'))
            self.eq('https://vertex.link/scans/FOO-10/0', nodes[0].get('ext:url'))

            self.len(1, await core.nodes('it:sec:vuln:scan:result :asset -> * +inet:server'))
            self.len(1, await core.nodes('it:sec:vuln:scan:result -> risk:vuln +:name=nucsploit9k'))
            self.len(1, await core.nodes('it:sec:vuln:scan:result -> risk:mitigation +:name="mitigate this"'))

    async def test_infotech_it_sec_metrics(self):

        async with self.getTestCore() as core:
            nodes = await core.nodes('''
                [ it:sec:metrics=*

                    :org={ gen.ou.org vertex }
                    :org:name=vertex
                    :org:fqdn=vertex.link

                    :period=(202307, 202308)

                    :alerts:count=100
                    :alerts:falsepos=90
                    :alerts:meantime:triage=2:00:00

                    :assets:users=13
                    :assets:hosts=123

                    :assets:vulns:count=4
                    :assets:vulns:mitigated=2
                    :assets:vulns:discovered=4
                    :assets:vulns:preexisting=2

                    :assets:vulns:meantime:mitigate="1D 2:37:00"

                ]
            ''')
            self.len(1, nodes)

            self.eq('vertex', nodes[0].get('org:name'))
            self.eq('vertex.link', nodes[0].get('org:fqdn'))
            self.eq((1688169600000, 1690848000000), nodes[0].get('period'))

            self.eq(100, nodes[0].get('alerts:count'))
            self.eq(90, nodes[0].get('alerts:falsepos'))
            self.eq(7200000, nodes[0].get('alerts:meantime:triage'))

            self.eq(13, nodes[0].get('assets:users'))
            self.eq(123, nodes[0].get('assets:hosts'))

            self.eq(4, nodes[0].get('assets:vulns:count'))
            self.eq(2, nodes[0].get('assets:vulns:mitigated'))
            self.eq(4, nodes[0].get('assets:vulns:discovered'))
            self.eq(2, nodes[0].get('assets:vulns:preexisting'))

            self.len(1, await core.nodes('it:sec:metrics -> ou:org +:name=vertex'))
