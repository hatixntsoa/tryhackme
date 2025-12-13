rule TBFC_Simple_MZ_Detect
{
    meta:
        author = "TBFC Blue Team Detection"
        description = "Extract TBFC Message fragments sent by McSkidy"
        date = "2025-10-10"
        confidence = "low"

    strings:
        $tbfc_msg = /TBFC:[A-Za-z0-9]+/ ascii

    condition:
        $tbfc_msg
}
