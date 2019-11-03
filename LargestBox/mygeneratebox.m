function re = mygeneratebox(coorfile,path,nameprefix)


    fpath=coorfile;


    coors=load(fpath);


    minx=min(coors(:,1));
    miny=min(coors(:,2));
    maxx=max(coors(:,1));
    maxy=max(coors(:,2));
 
    
    newindx=coors(:,1)-minx+1;
    newindy=coors(:,2)-miny+1;
    img=zeros(maxy-miny+1,maxx-minx+1);
    img(sub2ind(size(img),newindy,newindx))=1;


    BW=logical(img);



    S = FindLargestSquares(BW);
    [C H W] = FindLargestRectangles(BW, [0 0 1]);

    [~, pos] = max(C(:));
    [r c] = ind2sub(size(S), pos);

    [cl,ch]=size(C);
    C2=reshape(C,[1,cl*ch]);
    

    res=[r+miny-1,c+minx-1,W(r,c),H(r,c)];


    resname=[path,'\',nameprefix,'_image_largest_rec.csv'];


    header=['Y','X','W','H'];


    csvwrite(resname,header);

    dlmwrite (resname, res, '-append');

    
    re=resname;


end