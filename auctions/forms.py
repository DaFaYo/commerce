from decimal import Decimal
from django.forms import CharField, DecimalField, Form, ModelForm, NumberInput, Textarea
from auctions.models import Listing
from django.core.validators import MinValueValidator




class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "starting_bid", "photo", "categories"]  

        def __init__(self, *args, **kwargs):
            super(ListingForm, self).__init__(*args, **kwargs)
            self.fields["photo"].required = False
            self.fields["categories"].required = False

class NewBidForm(Form):
    bid = DecimalField(max_digits=10, decimal_places=2, 
            widget=NumberInput(attrs={'placeholder': 'Bid'}),
            validators=[MinValueValidator(Decimal('0.01'))])  

class NewCommentForm(Form):
    comment = CharField(widget=Textarea(attrs={'placeholder': 'Add comment'}))
          