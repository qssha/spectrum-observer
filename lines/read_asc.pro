; function for ASCII file reading
function READ_ASC,file,head,text=text
;file='n470_2n.fit'
;head=6
s=''

; if n_params() eq 1 then head=0
; determination of the column number

; s=0d
openr,u,file,/get_lun
if keyword_set(head) then for i=1,head do readf,u,s
readf,u,s
 ns=strtrim(strcompress(s),2)
 nc=n_elements(strsplit(ns,' ',/ext))
; close,u
;free_lun,u
;read file
if not(keyword_set(text)) then d=double(strsplit(ns,' ',/ext)) else d=strsplit(ns,' ',/ext)
; openr,u,file,/get_lun
if keyword_set(head) then for i=0,head-1 do readf,u,s
s=' '
while not(eof(u)) and (s ne '') do begin
readf,u,s
ns=strtrim(strcompress(s),2)
if ns ne '' then begin
  if not(keyword_set(text)) then d=[d,double(strsplit(ns,' ',/ext))] else d=[d,(strsplit(ns,' ',/ext))]
endif
endwhile
close,u
free_lun,u
;print,d
if not(keyword_set(text)) then d=reform(d(0:floor(double(n_elements(d))/double(nc))*nc-1),nc,n_elements(d)/nc)
return,d
END
