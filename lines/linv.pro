;; LinV 1.2 batch file 
;; activated by  /usr/local/itt/idladd/linv.dir/linv 
;; Authors: P. Abolmasov, O. Maryeva
;; send your comments and suggestions to pasha@sao.ru 
;; mind the paths! 
;; good luck ! 
; common fide, flist, dir, meds, runs, fact, avs, codedir, ver         ;; file list, directory, median and running average windows
common global, dir0, codedir0, ver0

print,'test 1 '
 
codedir0='/home/yulia/yulia/IDL/lib/linv.dir/'
dir0='~/'
ver0='1.2'


!PATH=codedir0+'/astrolib/:'+codedir0+':'+!PATH
resolve_all 
print,'test 2 '
view_sp
exit
