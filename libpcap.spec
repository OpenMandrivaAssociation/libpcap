%define major	1
%define libname	%mklibname pcap %{major}
%define devname	%mklibname pcap -d

Summary:	A system-independent interface for user-level packet capture
Name:		libpcap
Version:	1.4.0
Release:	5
License:	BSD
Group:		System/Libraries
Url:		http://www.tcpdump.org/
Source0:	http://www.tcpdump.org/release/%{name}-%{version}.tar.gz
Source1:	http://www.tcpdump.org/release/%{name}-%{version}.tar.gz.sig
Patch0:		libpcap-multilib.patch
Patch1:		libpcap-man.patch
Patch2:		lpthread-1.3.0-libpcap.patch
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	pkgconfig(bluez)
BuildRequires:	pkgconfig(libnl-3.0)

%description
Libpcap provides a portable framework for low-level network monitoring. Libpcap
can provide network statistics collection, security monitoring and network
debugging.  Since almost every system vendor provides a different interface for
packet capture, the libpcap authors created this system-independent API to ease
in porting and to alleviate the need for several system-dependent packet
capture modules in each application.

%package doc
Summary:	Manual pages for %{name}
Group:		Books/Other
BuildArch:	noarch
Conflicts:	%{devname} < 1.1.1-3

%description doc
This contains the manual pages documenting %{name}.

%package -n	%{libname}
Summary:	A system-independent interface for user-level packet capture
Group:		System/Libraries
Provides:	%{name} = %{version}-%{release}
Provides:	pcap = %{version}-%{release}

%description -n	%{libname}
Libpcap provides a portable framework for low-level network monitoring. Libpcap
can provide network statistics collection, security monitoring and network
debugging.  Since almost every system vendor provides a different interface for
packet capture, the libpcap authors created this system-independent API to ease
in porting and to alleviate the need for several system-dependent packet
capture modules in each application.

%package -n	%{devname}
Summary:	Development library and header files for the pcap library
Group:		Development/C
Requires:	%{libname} >= %{version}-%{release}
Provides:	pcap-devel = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description -n	%{devname}
This package contains the development pcap library and its header files needed
to compile applications such as tcpdump, etc.

%prep
%setup -q
%apply_patches

#sparc needs -fPIC 
%ifarch %{sparc}
sed -i -e 's|-fpic|-fPIC|g' configure
%endif

%build
export CFLAGS="%{optflags} -fno-strict-aliasing"
#export CFLAGS="%{optflags} -fPIC"

%configure2_5x \
	--disable-static \
	--enable-ipv6 \
	--enable-bluetooth \
	--with-pcap=linux

%make

%install
install -d %{buildroot}%{_bindir}

%makeinstall_std

# install additional headers
install -m0644 pcap-int.h %{buildroot}%{_includedir}/
install -m0644 pcap/bluetooth.h %{buildroot}%{_includedir}/pcap/

# nuke the statis lib
rm -f %{buildroot}%{_libdir}/libpcap.a

%files -n %{libname}
%{_libdir}/libpcap.so.%{major}*

%files doc
%{_mandir}/man5/pcap*
%{_mandir}/man7/pcap*

%files -n %{devname}
%doc README* CREDITS INSTALL.txt LICENSE CHANGES TODO
%{_bindir}/pcap-config
%dir %{_includedir}/pcap
%{_includedir}/pcap/*.h
%{_includedir}/*.h
%{_libdir}/libpcap.so
%{_mandir}/man1/pcap-config.1*
%{_mandir}/man3/pcap*

