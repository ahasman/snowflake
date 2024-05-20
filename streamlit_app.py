# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customise your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your smoothie!!!    
    """)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#Convert the Snowpark Dataframe to a Pandas Dataframe so we can us the LOC finction
pd_df=my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    ,my_dataframe
    ,max_selections=5
)
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # Join the list into a string

    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for', fruit_chosen, 'is', search_on, '.')

        # Get the nutritional info from Fruityvice API for the chosen fruit
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
        if fruityvice_response.ok:
            fv_df = pd.DataFrame(fruityvice_response.json())
            st.dataframe(fv_df, use_container_width=True)  # Display the nutritional info

    # Prepare the insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    #st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

import requests

