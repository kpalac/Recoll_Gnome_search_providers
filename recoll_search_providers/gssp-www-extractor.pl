#!/usr/bin/perl




#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Extract Firefox WWW history from SQLite DB to HTML file

use DBI;
use DBD::SQLite;



# Read config
my $home_dir = $ENV{"HOME"};
my $config = '';

if ( -f $home_dir.'/.config/gssp-recoll.conf' ) {
    open(my $fh, '<', $home_dir.'/.config/gssp-recoll.conf') or die "cannot open local config file (~/.config/gssp-recoll.config)";
    {
        local $/;
        $config = <$fh>;
    }
    close($fh);
}
elsif ( -f '/etc/gssp-recoll.conf' ) {
    open(my $fh, '<', '/etc/gssp-recoll.conf') or die "cannot open config file (/etc/gssp-recoll.conf)";
    {
        local $/;
        $config = <$fh>;
    }
    close($fh);

}


# Parse config
my $www_dir = '';
if ( $config =~ m/www_dir=(.*+)\n/ ) {
	$www_dir = $1;
        my $hd1 = '~/';
        my $hd2 = $home_dir.'/';
        $www_dir =~ s/$hd1/$hd2/ig;
}

# Check arguments
if ( not -d $www_dir ) { die "folder $www_dir does not exist"; }




# Get all Firefox databases for local user
my @dbs = glob($home_dir.'/.mozilla/firefox/*/places.sqlite');
my $dsn = '';

my $content_all = '';
my $content_item = '';



my $ipath = 0;


# Process each database
foreach my $db (@dbs) {

    if (not -f $db) { next }

    $dsn = "DBI:SQLite:dbname=$db";
    
    my $dbh = DBI->connect($dsn, '', '', { RaiseError => 1 }) or die $DBI::errstr;
    my $qr = qq(select url, title, description, preview_image_url, datetime(round(coalesce(last_visit_date,0)/1000000), 'unixepoch') from moz_places);
    my $sth = $dbh->prepare($qr);
    my $res = $sth->execute();

    my $dl = 0;

    while (my @row = $sth->fetchrow_array()) {

        $ipath += 1;

        $content_item = '

<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>
        <meta name="mime-type" content="text/html;charset=UTF-8"/>
        <meta name="date" content="'.$row[4].'"/>
        <meta name="title" content="'.$row[1].'"/>
        <meta name="image" content="'.$row[3].'"/>
        <meta name="filename" content="'.$row[0].'"/>
        <meta name="url" content="'.$row[0].'"/>
    </head>
    <body>
'.$row[1].'
'.$row[2].'
    </body>
</html>

';

        $dl = length($content_item);
        
        $content_all = $content_all.$content_item;
    }
    
    $dbh->disconnect();
}


$content_all = $content_all."\n";


# Write to the indexing buffer
my $buffer_file = $www_dir.'/firefox.www_hist';

open (FH, '>', $buffer_file) or die $!;
print FH $content_all;
close(FH);



