class file_box{
    constructor(el_name){
        this.el_name=el_name;
    }
    render_file_name(text){
        this.el_name.addEventListener("change",(e)=>{
        text.textContent=this.el_name.files.item(0).name;
        });

    }


}

