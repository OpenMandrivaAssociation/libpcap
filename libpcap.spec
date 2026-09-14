# libpcap is used by wine
%ifarch %{x86_64}
%bcond_without compat32
%else
%bcond_with compat32
%endif

# PGO trains the 64-bit library. 32-bit -m32 has no i386 Clang profile
# runtime, so compat32 is built without instrumentation.
%bcond_without pgo

%define major 1
%define libname %mklibname pcap %{major}
%define devname %mklibname pcap -d
%define lib32name %mklib32name pcap %{major}
%define dev32name %mklib32name pcap -d
%bcond_without bluetooth

# Upstream still trips over strict aliasing in the filter compiler
%global optflags %{optflags} -fno-strict-aliasing

Summary:	A system-independent interface for user-level packet capture
Name:		libpcap
Version:	1.11.0
Release:	1
License:	BSD
Group:		System/Libraries
Url:		https://www.tcpdump.org/
Source0:	https://www.tcpdump.org/release/%{name}-%{version}.tar.gz
Source1:	https://www.tcpdump.org/release/%{name}-%{version}.tar.gz.sig
Source2:	pgo-train.c
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	make
%if %{with bluetooth}
BuildRequires:	pkgconfig(bluez)
%endif
BuildRequires:	pkgconfig(libnl-genl-3.0)
%if %{with compat32}
BuildRequires:	libc6
# clang -m32 reads i386-*.cfg. The i686-openmandriva target has
# libclang_rt.profile.a and the sysroot lld needs in a fresh ABF chroot.
BuildRequires:	cross-i686-openmandriva-linux-gnu-clang
BuildRequires:	cross-i686-openmandriva-linux-gnu-libc
BuildRequires:	cross-i686-openmandriva-linux-gnu-gcc
BuildRequires:	cross-i686-openmandriva-linux-gnu-binutils
BuildRequires:	cross-i686-openmandriva-linux-gnu-kernel-headers
%endif

%description
Libpcap provides a portable framework for low-level network monitoring. Libpcap
can provide network statistics collection, security monitoring and network
debugging.  Since almost every system vendor provides a different interface for
packet capture, the libpcap authors created this system-independent API to ease
in porting and to alleviate the need for several system-dependent packet
capture modules in each application.

#----------------------------------------------------------------------------

%package doc
Summary:	Manual pages for %{name}
Group:		Documentation
BuildArch:	noarch

%description doc
This contains the manual pages documenting %{name}.

%files doc
%{_mandir}/man5/pcap*
%{_mandir}/man7/pcap*

#----------------------------------------------------------------------------

%package -n %{libname}
Summary:	A system-independent interface for user-level packet capture
Group:		System/Libraries
Provides:	pcap = %{EVRD}

%description -n %{libname}
Libpcap provides a portable framework for low-level network monitoring. Libpcap
can provide network statistics collection, security monitoring and network
debugging.  Since almost every system vendor provides a different interface for
packet capture, the libpcap authors created this system-independent API to ease
in porting and to alleviate the need for several system-dependent packet
capture modules in each application.

%files -n %{libname}
%{_libdir}/libpcap.so.%{major}*

#----------------------------------------------------------------------------

%package -n %{devname}
Summary:	Development library and header files for the pcap library
Group:		Development/C
Requires:	%{libname} = %{EVRD}
Provides:	pcap-devel = %{EVRD}

%description -n %{devname}
This package contains the development pcap library and its header files needed
to compile applications such as tcpdump, etc.

%files -n %{devname}
%doc README* CREDITS LICENSE CHANGES
%{_bindir}/pcap-config
%dir %{_includedir}/pcap
%{_includedir}/pcap/*.h
%{_includedir}/*.h
%{_libdir}/libpcap.so
%{_mandir}/man1/pcap-config.1*
%{_mandir}/man3/pcap*
%{_libdir}/pkgconfig/libpcap.pc

#----------------------------------------------------------------------------

%if %{with compat32}
%package -n %{lib32name}
Summary:	A system-independent interface for user-level packet capture
Group:		System/Libraries

%description -n %{lib32name}
Libpcap provides a portable framework for low-level network monitoring. Libpcap
can provide network statistics collection, security monitoring and network
debugging.  Since almost every system vendor provides a different interface for
packet capture, the libpcap authors created this system-independent API to ease
in porting and to alleviate the need for several system-dependent packet
capture modules in each application.

%files -n %{lib32name}
%{_prefix}/lib/libpcap.so.%{major}*

#----------------------------------------------------------------------------
%package -n %{dev32name}
Summary:	Development library and header files for the pcap library (32-bit)
Group:		Development/C
Requires:	%{lib32name} = %{EVRD}
Requires:	%{devname} = %{EVRD}

%description -n %{dev32name}
This package contains the development pcap library and its header files needed
to compile applications such as tcpdump, etc.

%files -n %{dev32name}
%{_prefix}/lib/libpcap.so
%{_prefix}/lib/pkgconfig/libpcap.pc
%endif

%prep
%setup -q

# 32-bit configure stays in %%prep so it never sees the PGO CFLAGS rpm
# injects around %%build. clang -m32 uses i386-pc-linux-gnu (no profile
# runtime); --target=i686-openmandriva-linux-gnu finds the sysroot.
# -I/usr/include is required so --enable-bluetooth sees bluez headers
# that live outside the i686 sysroot.
export CONFIGURE_TOP="$(pwd)"
%if %{with compat32}
mkdir build32
cd build32
CFLAGS="$(echo "${CFLAGS:-%{optflags}}" | sed -e 's/ -m64//g;s/ -mx32//g;s/ -flto//g;s/ -fprofile-[^ ]*//g;s/ -Wno-missing-profile//g') --target=i686-openmandriva-linux-gnu -I/usr/include" \
LDFLAGS="$(echo "${LDFLAGS:-%{build_ldflags}}" | sed -e 's/ -m64//g;s/ -mx32//g;s/ -flto//g;s/ -fprofile-[^ ]*//g;s/ -Wno-missing-profile//g') --target=i686-openmandriva-linux-gnu" \
%configure32 \
	--disable-rdma \
	--disable-dbus \
%if %{with bluetooth}
	--enable-bluetooth \
%endif
	--with-pcap=linux
cd ..
%endif

%build
export CONFIGURE_TOP="$(pwd)"

mkdir build
cd build
%configure \
	--disable-rdma \
	--disable-dbus \
%if %{with bluetooth}
	--enable-bluetooth \
%endif
	--with-pcap=linux
cd ..

%if %{with compat32}
%make_build -C build32
%endif
%make_build -C build

%if %{with pgo}
%pgo
# filtertest links the instrumented static library; pgo-train exercises
# savefile I/O and pcap_offline_filter.
%make_build -C build testprogs
ft=build/testprogs/filtertest
while IFS= read -r line; do
	[ -n "$line" ] || continue
	set -- $line
	dlt=$1
	shift
	"$ft" "$dlt" "$@" >/dev/null 2>&1 || :
done <<'EOF'
EN10MB tcp
EN10MB udp
EN10MB icmp
EN10MB arp
EN10MB ip
EN10MB ip6
EN10MB port 53
EN10MB port 80
EN10MB port 443
EN10MB tcp port 80
EN10MB tcp port 443
EN10MB udp port 53
EN10MB host 1.2.3.4
EN10MB net 10.0.0.0/8
EN10MB tcp and port 80
EN10MB not port 22
EN10MB vlan
EN10MB greater 64
EN10MB tcp[tcpflags] & (tcp-syn|tcp-fin) != 0
EN10MB udp port 53 or udp port 5353
LINUX_SLL tcp
LINUX_SLL udp port 53
LINUX_SLL2 ip or ip6
RAW tcp
IPV4 tcp port 443
PPP ip
IEEE802_11 ip
EOF
build/testprogs/findalldevstest >/dev/null 2>&1 || :
build/testprogs/versiontest >/dev/null 2>&1 || :

# Link the trainer to the instrumented static library (same as filtertest).
# -fno-lto avoids pulling profile symbols through shared LTO bitcode;
# -fprofile-generate supplies the Clang profile runtime.
%{__cc} -O2 -fno-lto -fprofile-generate=%{_pgo_profile_dir} -I. -o pgo-train %{S:2} \
	build/libpcap.a \
	$(sed -n 's/^LIBS = //p' build/Makefile)
./pgo-train
%endif

%install
install -d %{buildroot}%{_bindir}

%if %{with compat32}
%make_install -C build32
%endif

%make_install -C build

# wine still wants the private pcap-int.h
install -m0644 pcap-int.h %{buildroot}%{_includedir}/

# nuke the static lib
rm -f %{buildroot}%{_libdir}/libpcap.a %{buildroot}%{_prefix}/lib/libpcap.a
