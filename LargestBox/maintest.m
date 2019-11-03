clc;
clear all;

%uder linus it is / and under windows, it is \
%folder='Z:\NovemberNET\ACR\';
folder = '/Users/yanzhexu/Desktop/Research/SHHCC_ROI_TIFF';
subfs=dir(folder);


for i=3:length(subfs)
    %i=40 48;
    %i=40;
    tfol=subfs(i).name;
    fol=[folder,'/',tfol];
    
    subfs2=dir(fol);
%     if length(subfs2)==5
%         continue;
%     end
    
    
    for j=3:length(subfs2)
        
%         if subfs2(j).isdir~=1
%             continue;
%         end
        tfol2=subfs2(j).name;
        
        if strfind(tfol2,'Ph') == 1
        
            tfol2path = [fol,'/',tfol2];
            
            subfs3 = dir(tfol2path);
            for m = 1:length(subfs3)
                tfol3 = subfs3(m).name;
                if strfind(tfol3,'Lesion') == 1
                    tfol3path = [tfol2path,'/',tfol3];
                    coordpath = [tfol3path,'/coords.txt'];
                    
                    tpath = [tfol3path,'/'];
%             
                    nameprefix=tfol2;
                 
                    re=mygeneratebox(coordpath,tpath,nameprefix);
                end 
            end 
                    
        end 
        

        
    end
    
    
end

