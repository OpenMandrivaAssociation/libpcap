/*
 * PGO training for libpcap: typical compile/filter/savefile paths.
 * Live capture is skipped so the build does not need CAP_NET_RAW.
 */
#include <pcap/pcap.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

static void dummy(u_char *user, const struct pcap_pkthdr *h, const u_char *bytes)
{
	(void)user;
	(void)h;
	(void)bytes;
}

static const char *const filters[] = {
	"tcp",
	"udp",
	"icmp",
	"arp",
	"ip",
	"ip6",
	"port 53",
	"port 80",
	"port 443",
	"port 22",
	"tcp port 80",
	"tcp port 443",
	"udp port 53",
	"host 1.2.3.4",
	"src host 192.168.1.1",
	"dst host 10.0.0.1",
	"net 10.0.0.0/8",
	"net 192.168.0.0/16 and tcp",
	"tcp and port 80",
	"not port 22",
	"tcp or udp",
	"icmp or icmp6",
	"vlan",
	"greater 64",
	"less 1500",
	"portrange 0-1024",
	"broadcast",
	"multicast",
	"ip proto \\tcp",
	"ether proto \\ip",
	"tcp[tcpflags] & (tcp-syn|tcp-fin) != 0",
	"tcp dst port 443",
	"udp port 53 or udp port 5353",
	"src net 172.16.0.0/12",
	"dst port 22 or dst port 2222",
	NULL
};

static const int dlts[] = {
	DLT_EN10MB,
	DLT_LINUX_SLL,
	DLT_RAW,
	DLT_IPV4,
#ifdef DLT_LINUX_SLL2
	DLT_LINUX_SLL2,
#endif
#ifdef DLT_IPV6
	DLT_IPV6,
#endif
};

static uint8_t pkt_eth_ip_tcp[54];
static uint8_t pkt_eth_ip_udp[42];
static uint8_t pkt_eth_ip_icmp[42];
static uint8_t pkt_eth_arp[42];
static uint8_t pkt_eth_ip6_tcp[74];

static void put16(uint8_t *p, unsigned v)
{
	p[0] = (uint8_t)(v >> 8);
	p[1] = (uint8_t)v;
}

static void put32(uint8_t *p, unsigned v)
{
	p[0] = (uint8_t)(v >> 24);
	p[1] = (uint8_t)(v >> 16);
	p[2] = (uint8_t)(v >> 8);
	p[3] = (uint8_t)v;
}

static void eth(uint8_t *p, unsigned etype)
{
	memset(p, 0, 12);
	p[0] = 0x02;
	p[6] = 0x02;
	p[7] = 0x01;
	put16(p + 12, etype);
}

static void ipv4(uint8_t *p, unsigned proto, unsigned tot)
{
	p[0] = 0x45;
	p[1] = 0;
	put16(p + 2, tot);
	put16(p + 4, 0x1234);
	put16(p + 6, 0x4000);
	p[8] = 64;
	p[9] = (uint8_t)proto;
	p[10] = p[11] = 0;
	p[12] = 192; p[13] = 168; p[14] = 1; p[15] = 10;
	p[16] = 1; p[17] = 1; p[18] = 1; p[19] = 1;
}

static void make_packets(void)
{
	eth(pkt_eth_ip_tcp, 0x0800);
	ipv4(pkt_eth_ip_tcp + 14, 6, 40);
	put16(pkt_eth_ip_tcp + 34, 54321);
	put16(pkt_eth_ip_tcp + 36, 80);
	put32(pkt_eth_ip_tcp + 38, 1);
	put32(pkt_eth_ip_tcp + 42, 0);
	pkt_eth_ip_tcp[46] = 0x50;
	pkt_eth_ip_tcp[47] = 0x02;
	put16(pkt_eth_ip_tcp + 48, 8192);

	eth(pkt_eth_ip_udp, 0x0800);
	ipv4(pkt_eth_ip_udp + 14, 17, 28);
	put16(pkt_eth_ip_udp + 34, 12345);
	put16(pkt_eth_ip_udp + 36, 53);
	put16(pkt_eth_ip_udp + 38, 8);

	eth(pkt_eth_ip_icmp, 0x0800);
	ipv4(pkt_eth_ip_icmp + 14, 1, 28);
	pkt_eth_ip_icmp[34] = 8;
	pkt_eth_ip_icmp[35] = 0;

	eth(pkt_eth_arp, 0x0806);
	put16(pkt_eth_arp + 14, 1);
	put16(pkt_eth_arp + 16, 0x0800);
	pkt_eth_arp[18] = 6;
	pkt_eth_arp[19] = 4;
	put16(pkt_eth_arp + 20, 1);

	eth(pkt_eth_ip6_tcp, 0x86dd);
	pkt_eth_ip6_tcp[14] = 0x60;
	put16(pkt_eth_ip6_tcp + 18, 20);
	pkt_eth_ip6_tcp[20] = 6;
	pkt_eth_ip6_tcp[21] = 64;
	pkt_eth_ip6_tcp[22] = 0x20;
	pkt_eth_ip6_tcp[38] = 0x20;
	pkt_eth_ip6_tcp[54] = 0x01;
	put16(pkt_eth_ip6_tcp + 54, 44321);
	put16(pkt_eth_ip6_tcp + 56, 443);
	pkt_eth_ip6_tcp[66] = 0x50;
	pkt_eth_ip6_tcp[67] = 0x10;
}

static void dump_one(pcap_dumper_t *d, const uint8_t *pkt, unsigned len, unsigned n)
{
	struct pcap_pkthdr h;

	memset(&h, 0, sizeof(h));
	h.ts.tv_sec = 1700000000;
	h.ts.tv_usec = n;
	h.caplen = len;
	h.len = len;
	pcap_dump((u_char *)d, &h, pkt);
}

static void compile_filters(void)
{
	size_t i, j;

	for (i = 0; i < sizeof(dlts) / sizeof(dlts[0]); i++) {
		pcap_t *dead = pcap_open_dead(dlts[i], 65535);

		if (dead == NULL)
			continue;
		for (j = 0; filters[j] != NULL; j++) {
			struct bpf_program fp;
			int opt;

			for (opt = 1; opt >= 0; opt--) {
				if (pcap_compile(dead, &fp, filters[j], opt, PCAP_NETMASK_UNKNOWN) == 0)
					pcap_freecode(&fp);
			}
		}
		pcap_close(dead);
	}
}

static void savefile_io(const char *path)
{
	pcap_t *dead, *in;
	pcap_dumper_t *d;
	char errbuf[PCAP_ERRBUF_SIZE];
	size_t j;

	dead = pcap_open_dead(DLT_EN10MB, 65535);
	if (dead == NULL)
		return;
	d = pcap_dump_open(dead, path);
	if (d == NULL) {
		pcap_close(dead);
		return;
	}
	dump_one(d, pkt_eth_ip_tcp, sizeof(pkt_eth_ip_tcp), 1);
	dump_one(d, pkt_eth_ip_udp, sizeof(pkt_eth_ip_udp), 2);
	dump_one(d, pkt_eth_ip_icmp, sizeof(pkt_eth_ip_icmp), 3);
	dump_one(d, pkt_eth_arp, sizeof(pkt_eth_arp), 4);
	dump_one(d, pkt_eth_ip6_tcp, sizeof(pkt_eth_ip6_tcp), 5);
	dump_one(d, pkt_eth_ip_tcp, sizeof(pkt_eth_ip_tcp), 6);
	dump_one(d, pkt_eth_ip_udp, sizeof(pkt_eth_ip_udp), 7);
	pcap_dump_flush(d);
	pcap_dump_close(d);
	pcap_close(dead);

	in = pcap_open_offline(path, errbuf);
	if (in == NULL)
		return;
	pcap_loop(in, -1, dummy, NULL);
	pcap_close(in);

	for (j = 0; filters[j] != NULL; j++) {
		struct bpf_program fp;
		struct pcap_pkthdr *hdr;
		const u_char *data;
		int rc;

		in = pcap_open_offline(path, errbuf);
		if (in == NULL)
			break;
		if (pcap_compile(in, &fp, filters[j], 1, PCAP_NETMASK_UNKNOWN) == 0) {
			(void)pcap_setfilter(in, &fp);
			while ((rc = pcap_next_ex(in, &hdr, &data)) == 1) {
				(void)pcap_offline_filter(&fp, hdr, data);
			}
			pcap_freecode(&fp);
		}
		pcap_close(in);
	}
}

static void enumerate(void)
{
	pcap_if_t *devs = NULL;
	char errbuf[PCAP_ERRBUF_SIZE];
	bpf_u_int32 net, mask;

	(void)pcap_lib_version();
	(void)pcap_lookupnet("lo", &net, &mask, errbuf);
	if (pcap_findalldevs(&devs, errbuf) == 0 && devs != NULL)
		pcap_freealldevs(devs);
}

int main(void)
{
	const char *path = "pgo-train.pcap";

	make_packets();
	enumerate();
	compile_filters();
	savefile_io(path);
	unlink(path);
	return 0;
}
