package net.myngshj3.analysis.tool;

import java.lang.Object;
import java.lang.String;

public class Tester {

    private String _____s1_____ = "";

    private String _____m12_____ = "";

    public String _____m1_____() { return _____s1_____; }

    public void _____m9_____(String _____s1_____) {
        this._____s1_____ = _____s1_____;
    }
    public String _____m12_____() { return _____m12_____; }

    public void _____m15_____(String s) { this._____m12_____ = s; }

    public static void main(String[] args) {
        Tester obj = new Tester();
	obj._____m9_____("GXXXXX_NN");
	flowId = "GXXXXX_MM";
	obj._____m15_____(flowId);
        System.out.println(obj._____m1_____());
    }

}
