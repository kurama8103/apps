import streamlit as st
import tdnet_tool

def tdnet_render():
    st.title('tdnet PDFs Downloader')
    st.markdown('東証の適時開示情報閲覧サービスを検索し、PDFをダウンロードします。')
    st.markdown(
        "Link : [適時開示情報閲覧サービス](https://www.release.tdnet.info/inbs/I_main_00.html)",
        unsafe_allow_html=True)
    sel_code = st.text_input(label='keyword (example: 7203、経営計画、業績予想の修正)')
    if len(sel_code) == 0:
        return

    with st.spinner('Loading...'):
        td_ = tdnet(sel_code)
        df_ = td_.df
        if len(td_.df) != 0:
            df_['time'] = df_['time'].str[:5]
            dict_style = [
                dict(selector=".col3", props=[('min-width', '80px')]),
                dict(selector=".col4", props=[('min-width', '180px')])]
            st.dataframe(df_[['date', 'time', 'code', 'name', 'title', 'pdf']
                        ].style.set_table_styles(dict_style))


    if td_ is not None:
        if st.button('Download PDFs (TOP 10 files)'):
            with st.spinner():
                file=download(td_)
                st.download_button('download',file,mime='application/zip')
                # link = b64_file_to_href(file,'b')
                # st.markdown(link, unsafe_allow_html=True)

                # import streamlit.components.v1 as stc
                # import base64
                # src = base64.b64encode(file).decode()
                # stc.html(
                # "<script>window.open(\
                #     'data:application/zip;base64,{}')</script>".format(src)
                # )
                # stc.html(
                #     '<script>location.href={};</script>'.format(link)
                #         )
                
                

@st.cache_data(show_spinner=False)
def tdnet(sel_code):
    td = tdnet_tool.tdNet()
    td.getData_tdnet_KeywordSearch(sel_code)
    return td

@st.cache_data(show_spinner=False)
def download(td):
    # PDFダウンロード
    td.df.drop_duplicates(inplace=True)
    td.downloadPDF(limit=10)
    file_name = 'tdnet.zip'

    with open(file_name, "rb") as f:
        s = f.read()
    return s

def b64_file_to_href(file, mode='f'):
    import base64
    if mode == 'f':  # from file
        with open(file, "rb") as f:
            bytes_ = f.read()
    elif mode == 'b':  # direct bytes
        bytes_ = file
        file = 'file'
    b64 = base64.b64encode(bytes_).decode()
    href = f'<a href="data:application/zip;base64,{b64}" download={file}>download</a>'
    return href

tdnet_render()
