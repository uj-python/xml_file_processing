from django.shortcuts import render

from django.http.response import FileResponse
from django.core.files.storage  import FileSystemStorage

import xml.etree.ElementTree as ET
import xlsxwriter


def window(request):
    return render(request,'player/window.html')

def create_me(request):
     if request.method=='POST':   
        ip_file=request.FILES['ipfile']
        fs=FileSystemStorage()
        print("-----------",ip_file,type(ip_file.name),ip_file.name)
        fs.save(ip_file.name,ip_file)
        
        outworkbook=xlsxwriter.Workbook("./assets/files/out.xlsx")
        ot=outworkbook.add_worksheet()
        ippath="./media/"+ip_file.name;
        
        tree = ET.parse(ippath)
        root = tree.getroot()
        c=1
        cell_format = outworkbook.add_format({'bold': True})
        cell_format.set_align('center')
        cell_format.set_font_name('Cambria')



        
        header=['Date', 'Transaction Type', 'Vch No.', 'Ref No', 'Ref Type', 'Ref Date', 'Debtor', 'Ref Amount', 'Amount', 'Particulars', 'Vch Type', 'Amount Verified']
        ot.write_row(0,0,header)

        for i in root.iter('VOUCHER'):
            if i.attrib['VCHTYPE']=='Receipt':

                raw_date=i.find('DATE').text
                date=raw_date[6:8]+'-'+raw_date[4:6]+'-'+raw_date[0:4]

                vch_no=i.find('VOUCHERNUMBER').text
                main_name=i.find("PARTYLEDGERNAME").text

                for elem in i.iter('ALLLEDGERENTRIES.LIST'):
                    debtor=particulars=elem.find('LEDGERNAME').text
                    if debtor==main_name:
                        parent=True
                        trn_type="Parent"
                        amount_verified="NA"
                        cell=c
                    else:
                        trn_type="Other"
                        debtor=particulars=elem.find('LEDGERNAME').text
                        amount_verified="NA"
                    chk=amount=elem.find('AMOUNT').text
                    ref_amount="NA"
                    ref_type="NA"
                    ref_no="NA"
                    ref_date="NA"
                    
                    vch_type=i.find('VOUCHERTYPENAME').text

                    res=[date,trn_type,vch_no,ref_no,ref_type,ref_date,debtor,ref_amount,amount,particulars,vch_type,amount_verified]
                    ot.write_row(c,0,res)
                    c=c+1
                    sums=0

                    for q in elem.iter('BILLALLOCATIONS.LIST'):
                
                        if q.find("AMOUNT")!=None:
                            amount="NA"
                            ref_amount=q.find('AMOUNT').text
                            ref_type=q.find("BILLTYPE").text
                            ref_no=q.find('NAME').text
                            trn_type="Child"
                            ref_date=""
                            amount_verified="NA"
                            ref_date=""

                            debtor=particulars=i.find('PARTYLEDGERNAME').text
                            vch_type=i.find('VOUCHERTYPENAME').text
                            res=[date,trn_type,vch_no,ref_no,ref_type,ref_date,debtor,ref_amount,amount,particulars,vch_type,amount_verified]
                            ot.write_row(c,0,res)
                            c=c+1
                            sums=float(ref_amount)+sums;

                    if float(sums)==float(chk):
                        ot.write(cell,11,"YES")

        print("count=",c)
        outworkbook.close()
        

        f=open("./assets/files/out.xlsx",'rb')
        path="./assets/files/out.xlsx"
        resp = FileResponse(f)
        resp['Content-Disposition'] = 'attachment; filename="foo.xls"'

        return resp
