
use strict;
use warnings;

my $source = do{local$/;<>};
my $pos = 0;
my $mno = 0;
while ($pos < length($source)) {
    my $p = substr($source, $pos);
    if ($p =~ /((?P<SCOPE>(private|public|protected))\s+((?P<STATIC>static)\s+|)((?P<FINAL>final)\s+|)(?P<TYPE>((\w|[^\x00-\x7F\s])+\.)*(\w|[^\x00-\x7F\s])+)\s+(?P<NAME>(\w|[^\x00-\x7F\s])*[^\x00-\x7F\s]+(\w|[^\x00-\x7F\s])*)\s*\()/) {
	$mno++;
	my $segment = $1;
	my $scope = $+{SCOPE};
	$scope = "" unless defined($scope);
	my $static = $+{STATIC};
	$static = "" unless defined($static);
	my $final = $+{FINAL};
	$final = "" unless defined($final);
	my $type = $+{TYPE};
	my $name = $+{NAME};
	$pos += length($segment)-1;
	#print"$scope:$static:$final:$type:$name();\n";
	print"$name\t_____m${mno}_____\n";
    }
    elsif ($p =~ /([\.\s\(,;](?P<NAME>(\w|[^\x00-\x7F\s])*[^\x00-\x7F\s]+(\w|[^\x00-\x7F\s])*)\s*\()/) {
	$mno++;
	my $segment = $1;
	my $name = $+{NAME};
	print"$name\t_____m${mno}_____\n";
	$pos += length($segment);
    }
    else {
	last;
    }
}
