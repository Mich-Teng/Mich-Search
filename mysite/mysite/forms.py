from django import forms

class LargeTextareaWidget(forms.Textarea):
    def __init__(self,*args,**kwargs):
        kwargs.setdefault('attrs',{'class':'span5'}).update({'rows':10,'cols':100})
        super(LargeTextareaWidget,self).__init__(*args,**kwargs)

class CharFieldWidget(forms.TextInput):
    def __init__(self,holder,*args,**kwargs):
	    kwargs.setdefault('attrs',{'placeholder':holder,'class':'sign_input'}).update()
	    super(CharFieldWidget,self).__init__(*args,**kwargs)

class MyPasswordWidget(forms.PasswordInput):
    def __init__(self,holder,*args,**kwargs):
	    kwargs.setdefault('attrs',{'placeholder':holder,'class':'sign_input'}).update()
	    super(MyPasswordWidget,self).__init__(*args,**kwargs)

class DetailForm(forms.Form):
	name = forms.CharField(max_length=30,required=False,widget=CharFieldWidget(holder='name'))
	city = forms.CharField(max_length=60,required=False,widget=CharFieldWidget(holder='city'))
	province = forms.CharField(max_length=50,required=False,widget=CharFieldWidget(holder='province'))
	country = forms.CharField(max_length=50,required=False,widget=CharFieldWidget(holder='country'))
	description = forms.CharField(max_length=300,required=False,widget=LargeTextareaWidget)

	def __init__(self, *args, **kwargs):
		c =kwargs.pop('c')
		count = c['count']
		super(DetailForm, self).__init__(*args, **kwargs)
		for i in range(count):
			name = 'Favorite'+str(i+1)
			self.fields[name] = forms.CharField(label=name,required=False ,widget=CharFieldWidget(holder='Enter your favorite product'))

class ContactForm(forms.Form):
	subject = forms.CharField(max_length=100)
	email = forms.EmailField(required=False)
	message = forms.CharField(widget=LargeTextareaWidget)

class RegisterForm(forms.Form):
	user_name = forms.CharField(widget=CharFieldWidget(holder='user_name'), max_length=30,min_length=6)
	email = forms.EmailField(widget=CharFieldWidget(holder='email'), max_length=30)
	password = forms.CharField(max_length=30,min_length=6,widget=MyPasswordWidget(holder='password'))

