
use strict;
use warnings;

my $source = do{local$/;<>};
my $pos = 0;
my $sno = 0;
my @rules = ();
while ($pos < length($source)) {
    my $p = substr($source, $pos);
    if ($p =~ /(((?P<SCOPE>(private|public|protected|))\s+|)((?P<STATIC>static)\s+|)((?P<FINAL>final)\s+|)(?P<TYPE>((\w|[^\x00-\x7F\s])+\.)*(\w|[^\x00-\x7F\s])+)\s+(?P<NAME>(\w|[^\x00-\x7F\s])*[^\x00-\x7F\s]+(\w|[^\x00-\x7F\s])*)\s*\()/) {
	$sno++;
	my $segment = $1;
	my $scope = $+{SCOPE};
	$scope = "" unless defined($scope);
	my $static = $+{STATIC};
	$static = "" unless defined($static);
	my $final = $+{FINAL};
	$final = "" unless defined($final);
	my $type = $+{TYPE};
	my $name = $+{NAME};
	unless (grep {$_->[0] eq $name} @rules) {
	    push@rules,[$name,"_____s${sno}_____"];
	}
	$pos += length($segment)-1;
    }
    elsif ($p =~ /(((?P<SCOPE>(private|public|protected|))\s+|)((?P<STATIC>static)\s+|)((?P<FINAL>final)\s+|)(?P<TYPE>((\w|[^\x00-\x7F\s])+\.)*(\w|[^\x00-\x7F\s])+)\s+(?P<NAME>(\w|[^\x00-\x7F\s])*[^\x00-\x7F\s]+(\w|[^\x00-\x7F\s])*)\s*=)/) {
	$sno++;
	my $segment = $1;
	my $scope = $+{SCOPE};
	$scope = "" unless defined($scope);
	my $static = $+{STATIC};
	$static = "" unless defined($static);
	my $final = $+{FINAL};
	$final = "" unless defined($final);
	my $type = $+{TYPE};
	my $name = $+{NAME};
	unless (grep {$_->[0] eq $name} @rules) {
	    push@rules,[$name,"_____s${sno}_____"];
	}
	$pos += length($segment);
    }
    elsif ($p =~ /([\.\s\(,;](?P<NAME>(\w|[^\x00-\x7F\s])*[^\x00-\x7F\s]+(\w|[^\x00-\x7F\s])*)\s*\()/) {
	$sno++;
	my $segment = $1;
	my $name = $+{NAME};
	unless (grep {$_->[0] eq $name} @rules) {
	    push@rules,[$name,"_____s${sno}_____"];
	}
	$pos += length($segment);
    }
    else {
	last;
    }
}
@rules = sort { length($b->[0]) <=> length($a->[0]) } @rules;
for my $r (@rules) {
    print$r->[0],"\t",$r->[1],"\n";
}
