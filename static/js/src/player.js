/**
 * Created by RaPoSpectre on 4/27/16.
 */

$('.dropdown').dropdown({
    on: 'hover'
});


Vue.config.delimiters = ['${', '}}'];
new Vue({
    el: '#vChat',
    data: {
        query: '',
        classLoading: 'ui active inline loader'
    },
    methods: {
        getData: function (page) {
            if (this.query == '') {
                url = generateUrlWithToken('admin/api/chathistory') + '&page=' + page.toString();
            } else {
                url = generateUrlWithToken('admin/api/chathistory') + '&page=' + page.toString() + '&query=' + this.query;
            }
            this.$http.get(url, function (data) {
                if (data.status == 1) {
                    this.$set('chats', data.body.chathistory_list);
                    this.$set('pageObj', data.body.page_obj);
                }
                ;
            })
        }
    },
    ready: function () {
        this.getData(1);
    },
    computed: {
        noData: function () {
            return this.data.chats == undefined;
            //return true;
        }
    }
});